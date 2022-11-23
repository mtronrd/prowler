from lib.check.models import Check, Check_Report
from providers.aws.services.ec2.ec2_client import ec2_client
from providers.aws.services.ec2.lib.security_groups import check_security_group


class ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_elasticsearch_kibana_9200_9300_5601(
    Check
):
    def execute(self):
        findings = []
        check_ports = [9200, 9300, 5601]
        for security_group in ec2_client.security_groups:
            report = Check_Report(self.metadata())
            report.region = security_group.region
            report.resource_id = security_group.id
            report.status = "PASS"
            report.status_extended = f"Security group {security_group.name} ({security_group.id}) has not Elasticsearch/Kibana ports 9200, 9300 and 5601 open to the Internet."
            # Loop through every security group's ingress rule and check it
            for ingress_rule in security_group.ingress_rules:
                if check_security_group(
                    ingress_rule, "tcp", check_ports, any_address=True
                ):
                    report.status = "FAIL"
                    report.status_extended = f"Security group {security_group.name} ({security_group.id}) has Elasticsearch/Kibana ports 9200, 9300 and 5601 open to the Internet."
                    break
            findings.append(report)

        return findings
