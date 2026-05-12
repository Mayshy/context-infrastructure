# pontos 支持 HDFS 数据源接入

## TL;DR

> **Quick Summary**: 在 pontos 中新增 HDFS（CSV 格式）数据源类型，支持 Spark 全量同步，可选 cs_mafka 增量同步（复用现有路径），Kerberos 全局鉴权。对齐老云搜（joiner/naiads）行为。
>
> **Deliverables**:
> - `HdfsDataModel`（pontos-common）
> - `BatchDataEnum.hdfs` 暴露
> - `HdfsDataParser`（pontos-server）
> - `HdfsImporter`（pontos-full-sync-job）
> - `HdfsReader` Kerberos 支持（pontos-dal）
> - DB migration：`pontos_batch_data_meta` 新增 `hdfs_path`/`hdfs_file_prefix`/`hdfs_field_delimiter` 列
> - 前端 HDFS 注册 UI
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 (HdfsDataModel) → Task 4 (HdfsDataParser) → Task 5 (HdfsImporter) → Final Verification

---

## Context

### Original Request
为 pontos 支持 HDFS 类型的数据源接入，对齐老云搜（joiner/naiads）已有的 HDFS CSV 接入能力。

### Interview Summary
**Key Discussions**:
- 增量同步：复用 `StreamDataEnum.cs_mafka`，不需要新增实时 Job 逻辑
- Kerberos：全局共享，复用 joiner 的 `loginFromKeyTab` 逻辑
- 文件格式：仅 CSV（对齐老云搜）
- 分区感知：不支持（对齐老云搜）
- waitReady 机制：不需要（对齐老云搜）

**Research Findings**:
- pontos-server 用策略模式（`BatchDataParser`）管理各数据类型，新增 HDFS 只需实现一个 `HdfsDataParser` 并用 `@Component` 注册，`BatchDataParserFactory` 会自动发现
- `BatchDataMetaEntity`（`pontos_batch_data_meta` 表）无 HDFS 专用列，需要 DB migration（参考 S3 的 `s3bucket`/`s3path`）
- `pontos-realtime-sync-job` 的 `CsMafkaSourceReader` 已完整实现，HDFS 增量同步零 Job 改动
- `pontos-dal` 已有 `HdfsReader.java` 但无 Kerberos 鉴权，需补充
- `BatchDataParserFactory` 通过 Spring `ApplicationContext.getBeansOfType(BatchDataParser.class)` 自动注册，无需手动注册

---

## Work Objectives

### Core Objective
在 pontos 数据集成层新增 HDFS CSV 数据源类型，使业务方能通过 pontos 注册 HDFS 数据源、触发全量 Spark 同步，并可选接入 cs_mafka 增量同步，全程对齐老云搜行为。

### Concrete Deliverables
- `pontos-common`: `HdfsDataModel.java`、`BatchDataEnum.hdfs`、`BatchDataModel.hdfsType()`、`DataSourceModel` JsonSubTypes 注册
- `pontos-server`: `HdfsDataParser.java`、`BatchDataDTO` 新增 hdfs 字段、DB migration SQL
- `pontos-full-sync-job`: `HdfsImporter.java`、`ImporterFactory` 新增 case
- `pontos-dal`: `HdfsReader` 补充 Kerberos 支持、`HdfsStorageMeta` 补充字段
- 前端: HDFS 数据源注册 UI

### Definition of Done
- [ ] `mvn clean package -DskipTests` 构建成功（pontos 所有模块）
- [ ] `mvn test` 对应模块无 failure
- [ ] 能在 pontos 前端注册 HDFS 数据源（填写 hdfsPath/filePrefix/fieldDelimiter）
- [ ] 全量同步 Spark Job 能读取 HDFS CSV 文件并写入 Blade
- [ ] 增量同步可选择 cs_mafka 类型并填写 Topic

### Must Have
- `BatchDataEnum.hdfs` 加入 `getSupportedBatchDataEnums()` 列表（否则前端不可见）
- `HdfsDataModel` 注册到 `DataSourceModel` 的 `@JsonSubTypes`（否则反序列化失败）
- DB migration 先于服务代码上线（否则 `buildBatchDataMetaEntity` 写库报错）
- `HdfsImporter` 使用 `sparkSession.read().option("delimiter", fieldDelimiter).csv(hdfsPath)`（Spark 原生支持，无需 Hadoop 客户端）

### Must NOT Have (Guardrails)
- **不支持 Parquet/ORC**：文件格式仅 CSV，不做格式自动检测
- **不实现 waitReady**：`MirrorConfigServiceImpl` 中 `setWaitReady` 逻辑不修改
- **不实现分区感知**：hdfsPath 直接传给 Spark，不做分区路径解析
- **不新增实时 Job 代码**：`pontos-realtime-sync-job` 零改动，cs_mafka 路径完全复用
- **不在 HdfsDataParser 中调用外部 API 获取字段列表**：`getColumnInfoList()` 返回空列表，字段由用户手动填写（对齐 S3DataParser 行为）
- **不修改 joiner/naiads 代码**：本次仅改 pontos

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** - ALL verification is agent-executed.

### Test Decision
- **Infrastructure exists**: YES（Maven + JUnit）
- **Automated tests**: Tests-after（为新增的关键类补充单元测试）
- **Framework**: JUnit 4（Java 8 项目）

### QA Policy
每个 Task 包含 agent-executed QA scenarios。证据存入 `.sisyphus/evidence/`。

- **构建验证**: Bash（`mvn clean package -DskipTests`）
- **单元测试**: Bash（`mvn test -pl pontos-xxx`）
- **功能验证**: Bash（curl pontos API）

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1（立即开始，基础层，全部并行）:
├── Task 1: HdfsDataModel + BatchDataEnum + DataSourceModel 注册 [pontos-common] [quick]
├── Task 2: BatchDataDTO 新增 hdfs 字段 + BatchDataMetaEntity DB migration [pontos-server/dao] [quick]
└── Task 3: HdfsReader Kerberos 支持 + HdfsStorageMeta 补充字段 [pontos-dal] [quick]

Wave 2（Wave 1 完成后，核心逻辑，全部并行）:
├── Task 4: HdfsDataParser [pontos-server]（依赖 Task 1, 2）[unspecified-high]
└── Task 5: HdfsImporter + ImporterFactory [pontos-full-sync-job]（依赖 Task 1）[unspecified-high]

Wave 3（Wave 2 完成后）:
└── Task 6: 前端 HDFS 注册 UI（依赖 Task 4 API）[visual-engineering]

Wave FINAL（所有 Task 完成后，4 个并行 review）:
├── F1: Plan Compliance Audit [oracle]
├── F2: Code Quality Review [unspecified-high]
├── F3: Real Manual QA [unspecified-high]
└── F4: Scope Fidelity Check [deep]
→ 汇总结果 → 等待用户明确 okay
```

**Critical Path**: Task 1 → Task 4 → Task 6 → F1-F4
**Parallel Speedup**: ~60% faster than sequential
**Max Concurrent**: 3（Wave 1）

### Dependency Matrix

| Task | 依赖 | 被依赖 |
|------|------|--------|
| 1 | - | 4, 5 |
| 2 | - | 4 |
| 3 | - | 4（check 方法用 HdfsReader） |
| 4 | 1, 2, 3 | 6 |
| 5 | 1 | - |
| 6 | 4 | - |

---

## TODOs

> 实现 + 测试 = 一个 Task。每个 Task 必须包含：推荐 Agent Profile + 并行信息 + QA Scenarios。

---

- [ ] 1. **pontos-common — HdfsDataModel + BatchDataEnum.hdfs + DataSourceModel JsonSubTypes + BatchDataModel.hdfsType()**

  **What to do**:
  1. 新增 `HdfsDataModel.java`，继承 `BatchDataModel`，字段：`hdfsPath`（String）、`filePrefix`（String）、`fieldDelimiter`（String，默认 `,`）
  2. `BatchDataEnum` 新增枚举值 `hdfs("hdfs", "HDFS文件")`，并加入 `getSupportedBatchDataEnums()` 列表
  3. `DataSourceModel` 的 `@JsonSubTypes` 新增 `@JsonSubTypes.Type(value=HdfsDataModel.class, name="hdfs")`，并添加对应 import
  4. `BatchDataModel` 新增便捷方法 `public HdfsDataModel hdfsType() { return (HdfsDataModel) this; }`
  5. `DataSourceModel.parseRegion()` 的 switch 中，`hdfs` 走 `default` 分支返回 `Region.sh`（无需单独 case，已覆盖）

  **Must NOT do**:
  - 不添加 Parquet/ORC 相关字段
  - `fieldDelimiter` 不做枚举约束，保留 String 类型（对齐老云搜灵活性）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯 Java POJO + 枚举修改，无复杂逻辑
  - **Skills**: 无需额外 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Task 2、Task 3 并行）
  - **Blocks**: Task 4, Task 5
  - **Blocked By**: None（可立即开始）

  **References**:

  **Pattern References（直接复制结构）**:
  - `pontos-common/src/main/java/com/meituan/eagle/dataserver/common/model/datasource/batchdata/S3DataModel.java` — 完整参照模板：字段声明、`getPartOfDatasourceName()`、`getBatchMetaName()` 实现方式
  - `pontos-common/src/main/java/com/meituan/eagle/dataserver/common/model/datasource/batchdata/HiveDataModel.java` — `getShowInfo()` 实现参考
  - `pontos-common/src/main/java/com/meituan/eagle/dataserver/common/model/datasource/batchdata/BatchDataModel.java` — 在此文件新增 `hdfsType()` 方法，参考 `s3Type()` 写法（第 39-41 行）

  **Enum References**:
  - `pontos-common/src/main/java/com/meituan/eagle/dataserver/common/enums/BatchDataEnum.java` — 在此枚举新增 `hdfs("hdfs", "HDFS文件")`（参考 `s3("s3", "S3文件")` 第 28 行）；在 `getSupportedBatchDataEnums()` 第 51 行加入 `hdfs`

  **JsonSubTypes Reference**:
  - `pontos-common/src/main/java/com/meituan/eagle/dataserver/common/model/datasource/DataSourceModel.java` — 在 `@JsonSubTypes` 注解（第 35-43 行）新增 `@JsonSubTypes.Type(value=HdfsDataModel.class, name="hdfs")`；注意 S3DataModel 未在此注册（S3 走其他路径），HDFS 需要注册

  **HdfsDataModel 实现要点**:
  ```java
  // getPartOfDatasourceName(): hdfsPath 中 "/" 替换为 "."，去掉首尾点
  // getBatchMetaName(): "hdfs." + getPartOfDatasourceName()
  // getShowInfo(): "类型(HDFS文件)，路径(xxx)，前缀(xxx)"
  ```

  **Acceptance Criteria**:
  - [ ] `mvn clean package -DskipTests -pl pontos-common` BUILD SUCCESS
  - [ ] `BatchDataEnum.fromType("hdfs")` 返回 `BatchDataEnum.hdfs`（不返回 `none`）
  - [ ] `BatchDataEnum.getSupportedBatchDataEnums()` 包含 `hdfs`

  **QA Scenarios**:

  ```
  Scenario: BatchDataEnum.hdfs 可被正确解析
    Tool: Bash（mvn test -pl pontos-common）
    Steps:
      1. 在 pontos-common 目录运行: mvn clean test -pl pontos-common
      2. 检查 BatchDataEnumTest（若已有）或手动验证枚举值
    Expected Result: BUILD SUCCESS，无 test failure
    Evidence: .sisyphus/evidence/task-1-enum-test.txt

  Scenario: HdfsDataModel 反序列化不报错
    Tool: Bash（写一个临时 main 或 unit test）
    Preconditions: pontos-common 构建成功
    Steps:
      1. 构造 JSON: {"type":"hdfs","hdfsPath":"/user/test/","filePrefix":"part-","fieldDelimiter":","}
      2. 用 ObjectMapper.readValue() 反序列化为 BatchDataModel（通过 DataSourceModel 的 @JsonSubTypes）
      3. 断言结果 instanceof HdfsDataModel
    Expected Result: 反序列化成功，hdfsPath = "/user/test/"
    Evidence: .sisyphus/evidence/task-1-deserialization.txt
  ```

  **Commit**: YES（Wave 1 单独提交）
  - Message: `feat(pontos-common): add HdfsDataModel and BatchDataEnum.hdfs`
  - Files: `pontos-common/src/main/java/.../batchdata/HdfsDataModel.java`（新建），`BatchDataEnum.java`，`DataSourceModel.java`，`BatchDataModel.java`

---

- [ ] 2. **pontos-server/dao — BatchDataDTO 新增 hdfs 字段 + BatchDataMetaEntity 新增字段 + DB migration SQL**

  **What to do**:
  1. `BatchDataDTO.java` 新增三个字段：
     ```java
     // HDFS文件路径
     private String hdfsPath;
     // HDFS文件前缀（用于过滤目录下的文件）
     private String hdfsFilePrefix;
     // HDFS CSV字段分隔符，默认逗号
     private String hdfsFieldDelimiter;
     ```
  2. `BatchDataMetaEntity.java` 新增三个字段：
     ```java
     private String hdfsPath;
     private String hdfsFilePrefix;
     private String hdfsFieldDelimiter;
     ```
     （参考 `s3bucket`/`s3path` 字段，第 49-51 行）
  3. `pontos-server/src/ddl/datasource.sql` 末尾追加 migration SQL：
     ```sql
     ALTER TABLE pontos_batch_data_meta
       ADD COLUMN hdfs_path VARCHAR(1023) COMMENT 'HDFS文件路径',
       ADD COLUMN hdfs_file_prefix VARCHAR(255) COMMENT 'HDFS文件前缀',
       ADD COLUMN hdfs_field_delimiter VARCHAR(10) COMMENT 'HDFS CSV分隔符';
     ```

  **Must NOT do**:
  - 不修改已有字段（不改 s3bucket/s3path 等）
  - 不在 Entity 中添加任何业务逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯字段新增，无逻辑
  - **Skills**: 无需额外 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Task 1、Task 3 并行）
  - **Blocks**: Task 4
  - **Blocked By**: None（可立即开始）

  **References**:

  **Pattern References**:
  - `pontos-server/src/main/java/com/meituan/eagle/dataserver/request/BatchDataDTO.java` — 在此文件新增字段，参考 `s3bucket`/`s3path` 字段（第 33-36 行）的命名风格和注释格式
  - `pontos-dao/src/main/java/com/meituan/eagle/dataserver/domain/BatchDataMetaEntity.java` — 在此文件新增字段，参考 `s3bucket`/`s3path`（第 49-51 行）；注意 `@Table(name="pontos_batch_data_meta")` 对应数据库列名用下划线（`hdfs_path` → Java 字段 `hdfsPath`，MyBatis 自动映射）
  - `pontos-server/src/ddl/datasource.sql` — 在文件末尾追加 ALTER TABLE，参考最后一行 S3 的 ALTER（第 84-85 行）

  **Acceptance Criteria**:
  - [ ] `mvn clean package -DskipTests -pl pontos-server,pontos-dao` BUILD SUCCESS
  - [ ] `BatchDataDTO` 有 `hdfsPath`/`hdfsFilePrefix`/`hdfsFieldDelimiter` getter/setter（Lombok @Data 自动生成）
  - [ ] `datasource.sql` 末尾有 HDFS 相关 ALTER TABLE 语句

  **QA Scenarios**:

  ```
  Scenario: BatchDataDTO HDFS 字段可被 JSON 反序列化
    Tool: Bash（mvn clean package -DskipTests）
    Steps:
      1. 运行: export JAVA_HOME=... && mvn clean package -DskipTests -pl pontos-server,pontos-dao
      2. 确认 BUILD SUCCESS
    Expected Result: BUILD SUCCESS，无编译错误
    Evidence: .sisyphus/evidence/task-2-build.txt

  Scenario: datasource.sql 包含 HDFS migration
    Tool: Bash（grep）
    Steps:
      1. grep -n "hdfs_path" pontos-server/src/ddl/datasource.sql
    Expected Result: 找到 hdfs_path 相关 ALTER TABLE 行
    Evidence: .sisyphus/evidence/task-2-sql-check.txt
  ```

  **Commit**: YES（Wave 1 单独提交）
  - Message: `feat(pontos-server): add hdfs fields to BatchDataDTO and DB migration`
  - Files: `BatchDataDTO.java`，`BatchDataMetaEntity.java`，`datasource.sql`

---

- [ ] 3. **pontos-dal — HdfsReader 补充 Kerberos 支持 + HdfsStorageMeta 补充字段**

  **What to do**:
  1. `HdfsStorageMeta.java` 补充字段（当前只有 `hdfspath`，需补充）：
     ```java
     private String filePrefix;
     private String fieldDelimiter;
     // 补充 getter/setter（该类未使用 Lombok，需手动添加）
     ```
     同时补充 `hdfspath` 的 setter（当前只有 getter，第 21-23 行）
  2. `HdfsReader.java` 补充 Kerberos 登录逻辑，在 `smokingTest()` 和 `read()` 的 `FileSystem.get()` 调用**之前**加入：
     ```java
     // 复用 joiner HdfsUtil 的逻辑，在 pontos-dal 中新建 HdfsKerberosUtil 工具类
     // 读取 Lion Key：pontos.hdfs.security（boolean）、pontos.hdfs.confPath、pontos.hdfs.userName、pontos.hdfs.keytabFile、pontos.hdfs.krb5ConfigPath
     HdfsKerberosUtil.loginIfNeeded(configuration);
     ```
  3. 新建 `HdfsKerberosUtil.java`（与 `HdfsUtil.java` 结构一致，但 Lion Key 前缀改为 `pontos.hdfs.*`）：
     - `pontos.hdfs.security`（boolean，默认 false）
     - `pontos.hdfs.confPath`（默认 `/opt/meituan/hadoop/etc/hadoop`）
     - `pontos.hdfs.userName`（默认 `hadoop-muses`）
     - `pontos.hdfs.keytabFile`（默认 `/etc/hadoop/keytabs/hadoop-muses.keytab`）
     - `pontos.hdfs.krb5ConfigPath`（默认 `/opt/meituan/hadoop/etc/hadoop/krb5.conf`）

  **Must NOT do**:
  - 不删除现有的 `FileSystem.get(URI.create(hdfsPath), configuration)` 逻辑，Kerberos 是在它之前的前置登录步骤
  - 不修改 `MultiCloseableIterator` 内部逻辑

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 参照 joiner HdfsUtil 直接移植，逻辑清晰
  - **Skills**: 无需额外 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1（与 Task 1、Task 2 并行）
  - **Blocks**: Task 4（HdfsDataParser.check() 会调用 HdfsReader）
  - **Blocked By**: None（可立即开始）

  **References**:

  **Kerberos 逻辑参考（直接移植）**:
  - `joiner/collector/src/main/java/com/dp/arts/joiner/collector/util/HdfsUtil.java` — `loginFromKeyTab()` 方法（第 39-82 行）是完整的 Kerberos 登录逻辑，**直接复制并修改 Lion Key 前缀**（`Joiner.Hadoop.*` → `pontos.hdfs.*`）
  - 注意：joiner 使用 `NetworkUtil.getLocalHostName()`，pontos-dal 中需确认是否有同等工具；若无，可用 `InetAddress.getLocalHost().getHostName()` 替代（Java 标准库）

  **Files to Modify**:
  - `pontos-dal/src/main/java/com/meituan/eagle/dataserver/dal/meta/HdfsStorageMeta.java` — 补充字段和 setter（第 10-23 行现状：只有 `hdfspath` 字段和 getter）
  - `pontos-dal/src/main/java/com/meituan/eagle/dataserver/dal/readers/impl/HdfsReader.java` — 在 `smokingTest()`（第 41 行）和 `read()`（第 69 行）的 `new Configuration()` 之后、`FileSystem.get()` 之前，加入 `HdfsKerberosUtil.loginIfNeeded(configuration)`

  **New File**:
  - `pontos-dal/src/main/java/com/meituan/eagle/dataserver/dal/readers/impl/HdfsKerberosUtil.java`（参照 joiner HdfsUtil 结构）

  **Acceptance Criteria**:
  - [ ] `mvn clean package -DskipTests -pl pontos-dal` BUILD SUCCESS
  - [ ] `HdfsKerberosUtil.java` 存在，包含 `loginIfNeeded(Configuration conf)` 方法
  - [ ] `HdfsStorageMeta` 有 `filePrefix`/`fieldDelimiter` 字段及 getter/setter

  **QA Scenarios**:

  ```
  Scenario: pontos-dal 构建成功
    Tool: Bash
    Steps:
      1. 运行: export JAVA_HOME=/Users/shenhuayu/Library/Java/JavaVirtualMachines/corretto-1.8.0_452/Contents/Home && mvn clean package -DskipTests -pl pontos-dal
    Expected Result: BUILD SUCCESS
    Evidence: .sisyphus/evidence/task-3-build.txt

  Scenario: Kerberos disabled 时 HdfsReader 不报错（security=false 走 HADOOP_USER_NAME 路径）
    Tool: Bash（unit test 或构建验证）
    Preconditions: Lion pontos.hdfs.security 未配置（默认 false）
    Steps:
      1. 确认 HdfsKerberosUtil.loginIfNeeded() 在 security=false 时只调用 System.setProperty("HADOOP_USER_NAME", ...)
      2. Code review 确认无 NPE 风险
    Expected Result: 代码逻辑正确，无 NullPointerException 风险
    Evidence: .sisyphus/evidence/task-3-kerberos-logic.txt
  ```

  **Commit**: YES（Wave 1 单独提交）
  - Message: `feat(pontos-dal): add Kerberos support to HdfsReader and enrich HdfsStorageMeta`
  - Files: `HdfsStorageMeta.java`，`HdfsReader.java`，`HdfsKerberosUtil.java`（新建）

---

- [ ] 4. **pontos-server — HdfsDataParser（@Component 实现 BatchDataParser）**

  **What to do**:
  新建 `HdfsDataParser.java`，实现 `BatchDataParser` 的所有抽象方法：

  ```java
  @Component
  @Slf4j
  public class HdfsDataParser extends BatchDataParser {

      @Override
      public String getType() { return BatchDataEnum.hdfs.getType(); }

      @Override
      public List<StreamDataEnum> getSupportStreamDataTypeList() {
          return Arrays.asList(StreamDataEnum.cs_mafka, StreamDataEnum.none);
      }

      @Override
      public List<ColumnInfo> getColumnInfoList(BatchDataModel batchDataModel) {
          // HDFS 字段由用户手动填写，不做自动发现，对齐 S3DataParser
          return Collections.emptyList();
      }

      @Override
      public Region getRegion(BatchDataModel batchDataModel) { return null; }

      @Override
      public void check(BatchDataModel batchDataModel) {
          // 验证 hdfsPath 不为空，格式合法（以 hdfs:// 或 / 开头）
          HdfsDataModel model = batchDataModel.hdfsType();
          if (StringUtils.isBlank(model.getHdfsPath())) {
              throw new IllegalArgumentException("hdfsPath 不能为空");
          }
          // 不做实际网络连通性验证（对齐 HiveDataParser.check() 空实现）
      }

      @Override
      public HdfsDataModel buildModelByRequest(BatchDataDTO batchData) throws Exception {
          HdfsDataModel model = new HdfsDataModel();
          model.setHdfsPath(batchData.getHdfsPath());
          model.setFilePrefix(batchData.getHdfsFilePrefix());
          model.setFieldDelimiter(
              StringUtils.isBlank(batchData.getHdfsFieldDelimiter()) ? "," : batchData.getHdfsFieldDelimiter()
          );
          return model;
      }

      @Override
      public HdfsDataModel buildModelByEntity(BatchDataMetaEntity entity) {
          HdfsDataModel model = new HdfsDataModel();
          model.setHdfsPath(entity.getHdfsPath());
          model.setFilePrefix(entity.getHdfsFilePrefix());
          model.setFieldDelimiter(entity.getHdfsFieldDelimiter());
          return model;
      }

      @Override
      public BatchDataMetaEntity buildBatchDataMetaEntity(BatchDataModel batchDataModel) {
          HdfsDataModel model = batchDataModel.hdfsType();
          BatchDataMetaEntity entity = new BatchDataMetaEntity();
          entity.setType(model.getBatchDataEnum().getType());
          entity.setDataMeta(model.getBatchMetaName());
          entity.setHdfsPath(model.getHdfsPath());
          entity.setHdfsFilePrefix(model.getFilePrefix());
          entity.setHdfsFieldDelimiter(model.getFieldDelimiter());
          return entity;
      }

      @Override
      public BatchDataDTO buildBatchDataDTO(BatchDataModel batchDataModel) {
          HdfsDataModel model = batchDataModel.hdfsType();
          BatchDataDTO dto = new BatchDataDTO();
          dto.setBatchDataType(model.getBatchDataEnum().getType());
          dto.setHdfsPath(model.getHdfsPath());
          dto.setHdfsFilePrefix(model.getFilePrefix());
          dto.setHdfsFieldDelimiter(model.getFieldDelimiter());
          return dto;
      }
  }
  ```

  **Must NOT do**:
  - `check()` 不做实际 HDFS 连通性验证（不调用 HdfsReader，避免引入 Hadoop 客户端依赖到 pontos-server 模块）
  - `getColumnInfoList()` 不调用任何外部 API，直接返回空列表
  - 不新增 `suggestTable()` 实现（用默认空实现）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要理解 BatchDataParser 契约，正确实现所有方法，并确认 Spring 自动注册机制
  - **Skills**: 无需额外 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 5 并行）
  - **Parallel Group**: Wave 2（与 Task 5 并行，依赖 Task 1、2、3）
  - **Blocks**: Task 6（前端 API 依赖 Parser 注册成功）
  - **Blocked By**: Task 1（需要 HdfsDataModel、BatchDataEnum.hdfs）、Task 2（需要 BatchDataDTO/BatchDataMetaEntity hdfs 字段）

  **References**:

  **完整参照模板（S3DataParser）**:
  - `pontos-server/src/main/java/com/meituan/eagle/dataserver/service/batchdataparserimpl/S3DataParser.java` — 完整实现模板，HDFS 与 S3 行为高度相似（文件类型、无自动字段发现、getRegion()=null）
  - `pontos-server/src/main/java/com/meituan/eagle/dataserver/service/batchdataparserimpl/HiveDataParser.java` — `getSupportStreamDataTypeList()` 参考（第 68-72 行返回 `[cs_mafka, none]`，HDFS 应相同）

  **抽象基类契约**:
  - `pontos-server/src/main/java/com/meituan/eagle/dataserver/service/BatchDataParser.java` — 所有抽象方法签名，确认无遗漏

  **自动注册机制**:
  - `pontos-server/src/main/java/com/meituan/eagle/dataserver/service/impl/BatchDataParserFactory.java` — `@Component` 标注后自动被 `getBeansOfType(BatchDataParser.class)` 发现，**无需手动注册**

  **Acceptance Criteria**:
  - [ ] `mvn clean package -DskipTests -pl pontos-server` BUILD SUCCESS
  - [ ] `HdfsDataParser.java` 存在，有 `@Component` 注解
  - [ ] `getType()` 返回 `"hdfs"`
  - [ ] `getSupportStreamDataTypeList()` 包含 `cs_mafka` 和 `none`
  - [ ] `getColumnInfoList()` 返回空列表

  **QA Scenarios**:

  ```
  Scenario: pontos-server 构建成功，HdfsDataParser 被 Spring 正确加载
    Tool: Bash
    Steps:
      1. 运行: export JAVA_HOME=... && mvn clean package -DskipTests -pl pontos-server
    Expected Result: BUILD SUCCESS
    Evidence: .sisyphus/evidence/task-4-build.txt

  Scenario: 注册 HDFS 数据源 API 返回成功（需 pontos-server 本地启动 + DB migration 已执行）
    Tool: Bash（curl）
    Preconditions: pontos-server 本地启动（端口 8080），DB migration 已执行（hdfs_path 等列存在）
    Steps:
      1. curl -X POST http://localhost:8080/pontos/api/v1/ds/register \
           -H "Content-Type: application/json" \
           -d '{"batchDataType":"hdfs","hdfsPath":"/user/test/data/","hdfsFilePrefix":"part-","hdfsFieldDelimiter":",",...}'
      2. 检查响应 code=0，data.dataSource 包含 "hdfs."
    Expected Result: {"code":0,"data":{"dataSource":"hdfs.user.test.data."}}
    Evidence: .sisyphus/evidence/task-4-register-api.json

  Scenario: 查询支持的批数据类型列表包含 hdfs
    Tool: Bash（curl）
    Preconditions: pontos-server 本地启动
    Steps:
      1. curl http://localhost:8080/pontos/api/v1/suggest/batch_data_type
      2. 检查响应中包含 {"type":"hdfs","desc":"HDFS文件"}
    Expected Result: hdfs 出现在类型列表中
    Evidence: .sisyphus/evidence/task-4-suggest-types.json

  Scenario: check() 对空 hdfsPath 抛出异常
    Tool: Bash（mvn test）或 code review
    Steps:
      1. 确认 check() 方法在 hdfsPath 为 blank 时抛出 IllegalArgumentException
    Expected Result: 代码逻辑正确，有非空校验
    Evidence: .sisyphus/evidence/task-4-check-validation.txt
  ```

  **Commit**: YES（Wave 2 单独提交）
  - Message: `feat(pontos-server): add HdfsDataParser`
  - Files: `pontos-server/src/main/java/.../batchdataparserimpl/HdfsDataParser.java`（新建）

---

- [ ] 5. **pontos-full-sync-job — HdfsImporter + ImporterFactory case hdfs**

  **What to do**:
  1. 新建 `HdfsImporter.java`，继承 `Importer`：
     ```java
     public class HdfsImporter extends Importer {

         public HdfsImporter(SparkSession sparkSession, JavaSparkContext sparkContext,
                             DataSourceModel dataSourceModel, MirrorFlow mirrorFlow) {
             super(sparkSession, sparkContext, dataSourceModel, mirrorFlow);
         }

         @Override
         public BatchDataEnum getBatchDataType() { return BatchDataEnum.hdfs; }

         @Override
         public Dataset<Row> doImport() {
             HdfsDataModel model = (HdfsDataModel) dataSourceModel.getBatchDataModel();
             String hdfsPath = model.getHdfsPath();
             String fieldDelimiter = StringUtils.isBlank(model.getFieldDelimiter()) ? "," : model.getFieldDelimiter();

             log.info("HDFS import path: {}, delimiter: {}", hdfsPath, fieldDelimiter);

             return sparkSession.read()
                 .option("delimiter", fieldDelimiter)
                 .option("header", "false")
                 .csv(hdfsPath);
         }
     }
     ```
     注意：`filePrefix` 不用于 Spark 读取（Spark 直接读整个目录），filePrefix 只用于 pontos-dal 的 HdfsReader（增量同步路径）
  2. `ImporterFactory.java` 新增 case：
     ```java
     case hdfs:
         return new HdfsImporter(sparkSession, sparkContext, dataSourceModel, mirrorFlow);
     ```
     加在 `case s3:` 之前（若 s3 case 存在）或 `case hermes:` 之后

  **Must NOT do**:
  - 不添加 `option("inferSchema", "true")`（字段类型由 pontos 管理，不让 Spark 自动推断）
  - 不添加 `option("header", "true")`（HDFS 文件无 header 行，对齐老云搜行为）
  - 不修改 `pontos-realtime-sync-job` 任何文件

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: 需要理解 Spark Dataset API 和 Importer 框架
  - **Skills**: 无需额外 skill

  **Parallelization**:
  - **Can Run In Parallel**: YES（与 Task 4 并行）
  - **Parallel Group**: Wave 2（与 Task 4 并行，依赖 Task 1）
  - **Blocks**: 无（Task 6 前端不依赖 full-sync-job）
  - **Blocked By**: Task 1（需要 HdfsDataModel、BatchDataEnum.hdfs）

  **References**:

  **完整参照模板（HiveImporter）**:
  - `pontos-full-sync-job/src/main/java/com/meituan/eagle/dataserver/mirror/full/importer/HiveImporter.java` — 继承结构、构造函数签名、`getBatchDataType()`/`doImport()` 实现方式（第 1-45 行）
  - `pontos-full-sync-job/src/main/java/com/meituan/eagle/dataserver/mirror/full/importer/Importer.java` — 抽象基类，确认构造函数参数顺序（第 24-30 行）

  **ImporterFactory 修改位置**:
  - `pontos-full-sync-job/src/main/java/com/meituan/eagle/dataserver/mirror/full/importer/ImporterFactory.java` — 在 switch 语句（第 17-36 行）的 `default` 之前新增 `case hdfs:`

  **Spark CSV API 说明**:
  - `sparkSession.read().option("delimiter", fieldDelimiter).option("header", "false").csv(hdfsPath)` — 读取整个目录下所有文件，返回 `Dataset<Row>`，列名为 `_c0`, `_c1`, `_c2`...（无 header）
  - 对齐老云搜 HdfsCsvDataReader 的行为：读取目录下所有 filePrefix 匹配的文件，但 Spark 层不做前缀过滤（filePrefix 过滤是 DAL 层的增量同步行为）

  **Acceptance Criteria**:
  - [ ] `mvn clean package -DskipTests -pl pontos-full-sync-job` BUILD SUCCESS
  - [ ] `HdfsImporter.java` 存在，`getBatchDataType()` 返回 `BatchDataEnum.hdfs`
  - [ ] `ImporterFactory` 有 `case hdfs:` 分支
  - [ ] `doImport()` 使用 `sparkSession.read().option("delimiter", ...).csv(hdfsPath)`

  **QA Scenarios**:

  ```
  Scenario: pontos-full-sync-job 构建成功
    Tool: Bash
    Steps:
      1. 运行: export JAVA_HOME=... && mvn clean package -DskipTests -pl pontos-full-sync-job
    Expected Result: BUILD SUCCESS
    Evidence: .sisyphus/evidence/task-5-build.txt

  Scenario: ImporterFactory 对 hdfs 类型不抛 unsupported 异常
    Tool: Code review（grep）
    Steps:
      1. grep -n "case hdfs" pontos-full-sync-job/src/main/java/.../ImporterFactory.java
    Expected Result: 找到 "case hdfs:" 行
    Evidence: .sisyphus/evidence/task-5-factory-check.txt

  Scenario: HdfsImporter.doImport() 使用正确的 Spark CSV API
    Tool: Code review（grep）
    Steps:
      1. grep -n "sparkSession.read" pontos-full-sync-job/src/main/java/.../HdfsImporter.java
      2. 确认有 .option("delimiter", ...) 和 .csv(hdfsPath)
      3. 确认没有 .option("inferSchema", "true")
      4. 确认没有 .option("header", "true")
    Expected Result: Spark CSV 读取配置正确，无 inferSchema/header
    Evidence: .sisyphus/evidence/task-5-importer-review.txt
  ```

  **Commit**: YES（Wave 2 单独提交）
  - Message: `feat(pontos-full-sync-job): add HdfsImporter`
  - Files: `pontos-full-sync-job/src/main/java/.../importer/HdfsImporter.java`（新建），`ImporterFactory.java`

---

- [ ] 6. **前端 — HDFS 数据源注册 UI（调用 pontos REST API）**

  > ⚠️ **前提说明**：pontos 是纯后端服务，无前端代码。前端是独立项目（具体路径待确认）。
  > 本 Task 描述前端需要做的改动，执行前需确认前端项目位置。

  **What to do**:
  前端注册 HDFS 数据源时，需要在"批数据类型"选择 HDFS 后，展示三个额外输入字段：

  1. **HDFS 路径**（`hdfsPath`，必填）：HDFS 文件目录路径，例如 `/user/search/data/poi/`
  2. **文件前缀**（`hdfsFilePrefix`，选填）：目录下文件名前缀过滤，例如 `part-`（为空则读取所有文件）
  3. **字段分隔符**（`hdfsFieldDelimiter`，选填，默认 `,`）：CSV 字段分隔符

  **调用的 API**：
  - `GET /pontos/api/v1/registration/suggest/batch_data_type` — 获取支持的批数据类型列表（确认 hdfs 出现）
  - `POST /pontos/api/v1/registration/confirm` — 提交注册，`batchData` 字段中包含：
    ```json
    {
      "batchDataType": "hdfs",
      "hdfsPath": "/user/search/data/poi/",
      "hdfsFilePrefix": "part-",
      "hdfsFieldDelimiter": ","
    }
    ```

  **UI 交互逻辑**：
  - 当用户在批数据类型下拉框选择 "HDFS文件" 时，动态显示上述三个字段
  - 其他类型被选中时，隐藏这三个字段
  - 参考 S3 类型的 `s3bucket`/`s3path` 字段的显示/隐藏逻辑

  **Must NOT do**:
  - 不修改 pontos 后端代码（本 Task 纯前端）
  - 不添加 Parquet/ORC 格式选择
  - 不添加分区路径相关 UI

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: 前端 UI 新增表单字段，需要理解现有 UI 框架（Vue/React）和动态表单逻辑
  - **Skills**: 无需额外 skill

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3（依赖 Task 4 的 HdfsDataParser 注册成功，API 返回 hdfs 类型）
  - **Blocks**: 无
  - **Blocked By**: Task 4（需要 pontos-server 支持 hdfs 类型，`/suggest/batch_data_type` 返回 hdfs）

  **References**:

  **API 契约（关键）**:
  - `pontos/api-docs.json`（`/pontos/api/v1/registration/confirm`）— POST body 中 `batchData.batchDataType="hdfs"`，附带 `hdfsPath`/`hdfsFilePrefix`/`hdfsFieldDelimiter`
  - `pontos/api-docs.json`（`/pontos/api/v1/registration/suggest/batch_data_type`）— GET，返回支持的批数据类型列表，执行 Task 4 后应包含 `{"type":"hdfs","desc":"HDFS文件"}`

  **前端参考（S3 类型的实现方式）**:
  - `data-matrix/src/views/pontos/database/create/data-config.vue` — **主要改动文件**：第 312-345 行是 S3 字段的完整实现（`v-if="batchDataType === 's3'"`），HDFS 字段紧跟其后用相同模式添加；`data()` 中第 400-401 行是 `s3bucket`/`s3path` 初始化，HDFS 三个字段在此处初始化
  - `data-matrix/src/components/business/base-layout.vue` — 数据源详情展示：第 246-250 行是 S3 字段展示，HDFS 字段在此处新增只读展示
  - `data-matrix/src/views/hermes/navigation/detail.vue` — hermes 侧详情：第 250-254 行是 S3 字段展示，HDFS 字段在此处新增只读展示

  **Acceptance Criteria**:
  - [ ] 批数据类型下拉框包含 "HDFS文件" 选项
  - [ ] 选择 HDFS 后，显示 hdfsPath/hdfsFilePrefix/hdfsFieldDelimiter 三个输入框
  - [ ] 提交注册请求时，`batchData.batchDataType` 为 `"hdfs"`，三个字段正确传入

  **QA Scenarios**:

  ```
  Scenario: 前端选择 HDFS 类型后显示正确字段
    Tool: Playwright
    Preconditions: pontos 前端已启动，pontos-server 已启动（hdfs 类型已注册）
    Steps:
      1. 打开数据源注册页面
      2. 在批数据类型下拉框中选择 "HDFS文件"
      3. 断言页面出现 label 包含 "HDFS路径" 的 input 元素
      4. 断言页面出现 label 包含 "文件前缀" 的 input 元素
      5. 断言页面出现 label 包含 "字段分隔符" 的 input 元素
    Expected Result: 三个 HDFS 专属字段可见
    Evidence: .sisyphus/evidence/task-6-hdfs-form-visible.png

  Scenario: 提交 HDFS 数据源注册，API 请求体正确
    Tool: Playwright（拦截网络请求）
    Preconditions: 前端已启动，pontos-server 已启动
    Steps:
      1. 选择批数据类型 "HDFS文件"
      2. 填写 hdfsPath: "/user/test/data/"
      3. 填写 hdfsFilePrefix: "part-"
      4. 填写 hdfsFieldDelimiter: ","
      5. 填写其他必填字段（chineseName, appkey, categoryId 等）
      6. 点击提交按钮
      7. 拦截 POST /pontos/api/v1/registration/confirm 请求
      8. 断言请求体中 batchData.batchDataType == "hdfs"
      9. 断言请求体中 batchData.hdfsPath == "/user/test/data/"
    Expected Result: 请求体包含正确的 HDFS 字段
    Evidence: .sisyphus/evidence/task-6-register-request.json

  Scenario: 选择非 HDFS 类型时，HDFS 字段不显示
    Tool: Playwright
    Steps:
      1. 选择批数据类型 "Hive表"
      2. 断言不存在 label 包含 "HDFS路径" 的元素（或元素不可见）
    Expected Result: HDFS 字段隐藏
    Evidence: .sisyphus/evidence/task-6-hdfs-form-hidden.png
  ```

  **Commit**: YES（Wave 3 单独提交）
  - Message: `feat(frontend): add HDFS datasource registration UI`

---

## Final Verification Wave

> 4 个 review agent 并行运行，全部 APPROVE 后向用户汇报，等待明确 okay。

- [ ] F1. **Plan Compliance Audit** — `oracle`
  读取本计划所有 Must Have / Must NOT Have。逐条核查：Must Have 是否实现（读文件、curl API）；Must NOT Have 是否有违反（搜代码）；evidence 文件是否存在。
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  对所有改动文件：运行 `mvn clean package -DskipTests`；检查 `as any`/空 catch/注释代码/未用 import；检查 AI slop（过度注释、泛型命名 data/result/temp）；确认 Java 8 兼容（无 var、无 Stream.toList()）。
  Output: `Build [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F3. **Real Manual QA** — `unspecified-high`
  从干净状态执行所有 Task 的 QA Scenario：curl 注册 HDFS 数据源 API；curl 查询数据源详情确认字段；curl 触发全量同步并确认 Spark Job 参数正确；验证增量同步选项 cs_mafka 可选。保存响应到 `.sisyphus/evidence/final-qa/`。
  Output: `Scenarios [N/N pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  对每个 Task：读"What to do"，读实际 git diff，确认 1:1 对应——spec 里有的都实现了，spec 外的没有多写。检查 Must NOT do 合规（无 Parquet、无 waitReady、无实时 Job 改动）。
  Output: `Tasks [N/N compliant] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Commit Strategy

- Wave 1: `feat(pontos-common): add HdfsDataModel and BatchDataEnum.hdfs` — pontos-common
- Wave 1: `feat(pontos-server): add hdfs fields to BatchDataDTO and DB migration` — pontos-server/dao
- Wave 1: `feat(pontos-dal): add Kerberos support to HdfsReader` — pontos-dal
- Wave 2: `feat(pontos-server): add HdfsDataParser` — pontos-server
- Wave 2: `feat(pontos-full-sync-job): add HdfsImporter` — pontos-full-sync-job
- Wave 3: `feat(frontend): add HDFS datasource registration UI`

---

## Success Criteria

```bash
# 构建成功
mvn clean package -DskipTests  # Expected: BUILD SUCCESS

# 注册 HDFS 数据源（需 pontos-server 启动）
curl -X POST http://localhost:8080/pontos/api/v1/ds/register \
  -H "Content-Type: application/json" \
  -d '{"batchDataType":"hdfs","hdfsPath":"/user/test/data/","hdfsFilePrefix":"part-","hdfsFieldDelimiter":","}'
# Expected: {"code":0, "data":{"dataSource":"hdfs...."}}

# 查询支持的数据源类型（hdfs 应在列表中）
curl http://localhost:8080/pontos/api/v1/suggest/batch_data_type
# Expected: 响应中包含 {"type":"hdfs","desc":"HDFS文件"}
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent（无 Parquet/waitReady/实时 Job 改动）
- [ ] `mvn clean package -DskipTests` BUILD SUCCESS
- [ ] `mvn test` 新增单元测试通过
