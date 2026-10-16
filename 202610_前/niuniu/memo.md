按照我下面的描述，制作一份用于日本IT本番作业的手顺，要求简单易懂。 整体逻辑清晰。

作业描述：

目的： 在本番室搭建本地LLM， 各team的作业人员可以通过浏览器使用Ai chat画面。

概要： 我们准备了3台物理机器， 一台windows 物理机， 两台nvidia dgx spark gpu物理机。
由于本番室作业的严格性， 这三台机器一旦搬进本番室， 就不好拿出来了， 拿出来的话需要初始化机器。而且本番室是完全没有互联网的环境。
那么，我们就需要在搬进本番室之前，每台机器的各种设定要做好，搬进本番室后， 直接开始部署作业。
所以， 整个手顺分为两大部分， 1. 进入本番室前的作业 2. 进入本番室后的作业

作业一览：
1. 进入本番室前的作业

1.1 windows物理机的设定

- 初期化设定完成
  user创建， ip设置
- 连接互联网
- 安装必备软件
- wsl2 加 ubuntu24的安装
- ubuntu中 初期设定完成， 安装docker， 并且事先下载好docker image, litellm , postgresql , openwebui 
- docker compose 配置文件的作成  


1.2 两台dgx spark的设定
- 初期化设定完成
  user创建， ip设置
- 连接互联网
- os update
- 安装docker ， 并事先下载docker image vllm-openai
- ai model的下载
- docker compose 配置文件的作成 




2. 进入本番室后的作业

1.0 把三个机器插好网线和电源并且开机


1.2windows物理机的设定

- login进入windows
- 配置ipv4地址
- 确保和dgx spark的网络互通
- ssh 进入两个dgx spark， 并启动vllm
- 验证vllm 启动成功
- 进入wsl ubuntu， 移动到作业目录下， 先启动litellm
- 验证litellm启动成功， 并且能够连接两个vllm model。
- 启动openwebui，连接litellm ， 和AI对话， 动作确认
- openwebui的本番利用设定
- 使用本番室pc， 验证AI chat画面可以使用






