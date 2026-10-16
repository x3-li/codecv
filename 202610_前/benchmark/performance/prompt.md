# LLM性能测试方针报告模板的制作

## 目的
guidellm出力的结果做成日文报告， 首先应该确认报告模板， 具体参照`结果报告做成format`

## 背景
在一家日本IT公司的内网环境， 部署了一台Nvidia Dgx Spark服务器， CPU和GPU统一内存128GB。
使用这个服务器来部署Huggingface上下载的开源大模型，面向公司内部使用， 最大同时使用人数大概20人。
所以，希望通过性能测试，了解LLM的性能和吞吐量如何。
系统构成:vllm + litellm， 一次启动一个model

## LLM准备
- gemma4-26B-A4B-it
- gemma4-31B-it

## 性能测试tool
采用GuideLLM, 官网地址[guidellm](https://github.com/vllm-project/guidellm)。

## guidellm参数配置
- `Benchmark Profiles (--profile)`这个参数可选值很多， 这次采用`concurrent`， 测试并发1,2,5,10,15,20,30的结果
- `--data`， 设置prompt_tokens,output_tokens，找一个合适的值

## 结果报告做成format

0. 测试配置以及运行状况

1. 各concurrent的吞吐量分析表
- 并发数
- 请求速率
- input token/s
- output token/s
- 平均每个request output token/s
- 总token/s

2. 各concurrent的请求延迟分析
- TTFT
- request延迟 
- Itl mdn 
- tpop mdn

3. 日语综合分析