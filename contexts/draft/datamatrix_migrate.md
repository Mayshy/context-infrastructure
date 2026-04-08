参考信息：
1. 学城文档（其中代码细节、接口方面是过时的，只能参考它的逻辑思路）：
   1. https://km.sankuai.com/collabpage/2720531136
   2. https://km.sankuai.com/collabpage/2731488796
   3. https://km.sankuai.com/collabpage/2733380176
2. 代码仓库: 
   1. datamatrix:参考知识库contexts/projects/datamatrix-kb
   2. 老云搜:/Users/shenhuayu/Desktop/Project/naiads

目标：把老云搜的云搜应用迁移到datamatrix。完成47个应用完成数据校验，其中至少有22个应用已切流。
* 云搜应用：参考https://km.sankuai.com/collabpage/2713944610，可以理解为支持多个、多种类型的数据源ETL并输出到ES索引的服务。
* 完成数据校验：参考https://km.sankuai.com/collabpage/2733380176，完成数据校验在过去大多数时候需要我自己完成迁移并手动校验，少数时候老云搜应用对应的用户自己会进行迁移并校验。
* 应用已切流：切流是指用户把他的客户端流量从老云搜对应的ES索引切换到datamatrix对应的ES索引的过程。
* 老云搜和新云搜的架构差异：老云搜是单机服务、直接采集多个数据源的数据并处理后输出；datamatrix是分布式服务，数据流主干分为dataserver(pontos),modelserver(hermes),indexserver(kugget)这3个服务，其中modelserver不直接对接数据源、而是处理dataserver产生的数据镜像，datamatrix的全量同步过程在Spark上完成、增量同步过程在Flink上完成。
* 局限性：老云搜的数据建模关系在datamatrix不是100%支持，存在极少数不对应场景需要人工处理。

现状：我的手动迁移流程：需要检查老云搜复杂的配置，把它转换到datamatrix的格式并配置。这不是一个简单的一次性转换，因为老云搜和新云搜架构不同：这需要在datamatrix平台上操作数据集成(对应dataserver)生成每个数据源的数据镜像、操作数据建模(modelserver)生成若干个数据源按建模关系处理后对应的Hbase宽表、操作数据计算(对应indexserver)生成ES索引。

我的困难：手动挨个处理上述过程，过于繁琐，尤其体现在 
1. 问题1:管理如此多个链路的迁移、校验、沟通状态过于繁琐。
2. 问题2:数据建模中各个数据源的关系复杂，人工处理负担高；
3. 问题3:数据校验：当前人工校验过程繁琐，需要在多个页面间来回跳转；




你的任务：
1. 在contexts/projects下新建并维护一个datamatrix_migrate项目，在此持续迭代你的认知
2. 针对问题1，给出管理方案，我来决策
先完成上述两个任务，后续我再跟你讨论进一步的问题。


------

补充信息：
* 老云搜配置示例：
* 新datamatrix配置：