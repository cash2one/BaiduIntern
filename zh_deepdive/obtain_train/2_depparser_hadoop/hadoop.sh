#!/bin/bash

INPUT="/app/ps/spider/kg-value/wangjianxiang01/data/SPO_train_sentence_split"
#INPUT="/app/ps/spider/kg-value/wangjianxiang01/data/tmp"
OUTPUT="/app/ps/spider/kg-value/wangjianxiang01/data/SPO_train_depparser"

hadoop fs -rmr ${OUTPUT}

hadoop streaming \
    -input "${INPUT}"  \
    -output "${OUTPUT}" \
    -mapper "sh -x doParse.sh" \
    -reducer "NONE" \
    -file "doParse.sh" \
    -cacheArchive "/app/ps/spider/kg-value/wangjianxiang01/tools.tar.gz#." \
    -jobconf mapred.job.priority="VERY_HIGH" \
    -jobconf stream.num.map.output.key.fields=8 \
    -jobconf mapred.output.compress=true \
    -jobconf mapred.compress.map.output=true \
    -jobconf mapred.map.tasks=2000 \
    -jobconf mapred.job.map.capacity=300 \
    -jobconf mapred.reduce.tasks=0 \
    -jobconf mapred.job.reduce.capacity=300 \
    -jobconf mapred.job.name="wangjianxiang_depparser_hadoop"
