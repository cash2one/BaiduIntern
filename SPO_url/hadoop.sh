#!/bin/bash

# 先打包, 上传至 hadoop ...
tar zcf qdh.tar.gz ba shipin tuPian xiaoShuo xiazai yinpin jiefeng main.py
hadoop fs -rm /app/ps/spider/kg-value/wangjianxiang01/qdh.tar.gz
hadoop fs -put qdh.tar.gz /app/ps/spider/kg-value/wangjianxiang01/

INPUT="/app/ps/spider/wdm-site-offline/relation-extraction/dom_extraction/qiandaohu"
OUTPUT="/app/ps/spider/kg-value/wangjianxiang01/data/qiandaohu_10ku_spo"

hadoop fs -rmr ${OUTPUT}

hadoop streaming \
    -input "${INPUT}"  \
    -output "${OUTPUT}" \
    -mapper "main.py" \
    -reducer "NONE" \
    -cacheArchive "/app/ps/spider/kg-value/wangjianxiang01/qdh.tar.gz#." \
    -cacheArchive "/app/ps/spider/kg-value/wangjianxiang01/python.tar.gz#." \
    -jobconf mapred.job.priority="VERY_HIGH" \
    -jobconf mapred.textoutputformat.ignoreseparator=true \
    -jobconf stream.num.map.output.key.fields=5 \
    -jobconf mapred.output.compress=true \
    -jobconf mapred.compress.map.output=true \
    -jobconf mapred.map.tasks=3000 \
    -jobconf mapred.job.map.capacity=300 \
    -jobconf mapred.reduce.tasks=0 \
    -jobconf mapred.job.reduce.capacity=300 \
    -jobconf mapred.map.max.attempts=10 \
    -jobconf mapred.max.map.failures.percent="1" \
    -jobconf mapred.job.name="wangjianxiang_qdh"

#    -file "main.py" \

