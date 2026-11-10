#!/usr/bin/env bash
# OpenSearch health snapshot from CloudWatch (AWS/ES namespace).
set -euo pipefail
R=ap-southeast-1
HOURS=${1:-6}
PERIOD=${2:-300}
D=$(aws opensearch list-domain-names --region $R --query "DomainNames[0].DomainName" --output text)
A=$(aws sts get-caller-identity --query Account --output text)

aws opensearch describe-domain --region $R --domain-name "$D" \
  --query "DomainStatus.{domain:DomainName,type:ClusterConfig.InstanceType,count:ClusterConfig.InstanceCount,processing:Processing,state:DomainProcessingStatus}" \
  --output table

METRICS="ClusterStatus.green:Maximum ClusterStatus.yellow:Maximum ClusterStatus.red:Maximum Nodes:Minimum
CPUUtilization:Maximum JVMMemoryPressure:Maximum SysMemoryUtilization:Maximum FreeStorageSpace:Minimum
ClusterIndexWritesBlocked:Maximum AutomatedSnapshotFailure:Maximum ThreadpoolSearchRejected:Sum
ThreadpoolWriteRejected:Sum SearchLatency:Average IndexingLatency:Average SearchRate:Average
IndexingRate:Average 5xx:Sum JVMGCOldCollectionCount:Maximum OpenSearchRequests:Sum
Shards.unassigned:Maximum Shards.active:Maximum"

q=""; i=0
for m in $METRICS; do
  n=${m%%:*}; s=${m##*:}; i=$((i+1))
  q="$q{\"Id\":\"m$i\",\"Label\":\"$n/$s\",\"MetricStat\":{\"Metric\":{\"Namespace\":\"AWS/ES\",\"MetricName\":\"$n\",\"Dimensions\":[{\"Name\":\"DomainName\",\"Value\":\"$D\"},{\"Name\":\"ClientId\",\"Value\":\"$A\"}]},\"Period\":$PERIOD,\"Stat\":\"$s\"}},"
done

aws cloudwatch get-metric-data --region $R \
  --start-time "$(date -u -v-${HOURS}H +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --metric-data-queries "[${q%,}]" --output json |
python3 -I -c '
import json, sys
for r in json.load(sys.stdin)["MetricDataResults"]:
    lab = r["Label"]
    if not r["Values"]:
        print(f"{lab:36} NO DATA"); continue
    pts = sorted(zip(r["Timestamps"], r["Values"]))
    v = [x for _, x in pts]
    print(f"{lab:36} now={v[-1]:<10.2f} min={min(v):<10.1f} max={max(v):<10.1f} avg={sum(v)/len(v):.1f}")
'
