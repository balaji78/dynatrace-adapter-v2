import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DynatraceAPI:

    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.api_token = api_token

    def get_headers(self):
        return {
            'Authorization': f'Api-Token {self.api_token}',
            'Content-type': 'application/json'
        }

    # Get applications
    def get_applications(self):
        entity_selector = 'type(APPLICATION)'
        url = f'{self.base_url}entities?entitySelector={entity_selector}&from=now-1y&to=now'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()

    # Get applications by Management Zone
    def get_applications_by_management_zone(self, mzname):
        entity_selector = f'type(APPLICATION),mzName("{mzname}")'
        url = f'{self.base_url}entities?entitySelector={entity_selector}&from=now-1y&to=now'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()

    # Get hosts by management zone
    def get_hosts_by_management_zone(self, mzname):
        entity_selector = f'type(HOST),mzName("{mzname}")'
        url = f'{self.base_url}entities?entitySelector={entity_selector}&from=now-1y&to=now'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()
    
    # Get hosts by management zone Id
    def get_hosts_by_management_zoneId(self, mzId):
        entity_selector = f'type(HOST),mzId("{mzId}")'
        url = f'{self.base_url}entities?entitySelector={entity_selector}&from=now-1y&to=now'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()
    
    # Get host details
    def get_host_info(self, host_id):
        entity_selector = f'entities/{host_id}'
        url = f'{self.base_url}{entity_selector}'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        host_properties = response.json()['properties']
        host_info = {
            'hostName': host_properties['detectedName'],
            'osType': host_properties['osType'],
            'hypervisorType': host_properties['hypervisorType'],
            'virtualCpus': host_properties['virtualCpus'] if(host_properties['osType'] == 'AIX') else host_properties['cpuCores'],
            'logicalCpus': host_properties['logicalCpus'] if(host_properties['osType'] == 'AIX') else host_properties['logicalCpuCores'],
            'memoryTotal': host_properties['memoryTotal']
        }
        return host_info

    def get_host_details_by_management_zoneId(self, mzId):
        entity_selector = f'type(HOST),mzId("{mzId}")'
        url = f'{self.base_url}entities?entitySelector={entity_selector}&from=now-1y&to=now'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        hosts = response.json()

        for h in hosts['entities']:
            host_info = self.get_host_info(h['entityId'])
            h.update(host_info)
        
        return hosts
    
    def get_processes_for_host(self, host_id, from_ts, to_ts):
        entity_selector = 'type(PROCESS_GROUP_INSTANCE)'
        host_filter = f'fromRelationships.isProcessOf(type(HOST),entityId({host_id})))'
        time_filter = f'from={from_ts}&to={to_ts}'
        url = f'{self.base_url}entities?entitySelector={entity_selector},{host_filter}&{time_filter}'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()

    def get_services_by_process_id(self, process_id, from_ts, to_ts):
        entity_selector = 'type(SERVICE)'
        process_filter = f'fromRelationships.runOnProcessGroupInstance(entityId({process_id}))'
        time_filter = f'from={from_ts}&to={to_ts}'
        url = f'{self.base_url}entities?entitySelector={entity_selector},{process_filter}&{time_filter}'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()

    def get_metrics(self, entity_id, metrics, from_ts, to_ts, resolution = '1m'):
        entity_selector = f'entityId({entity_id})'
        metrics_selector = f'metricSelector=({metrics})'
        time_filter = f'from={from_ts}&to={to_ts}'
        url = f'{self.base_url}metrics/query?entitySelector={entity_selector}&{metrics_selector}&resolution={resolution}&{time_filter}'
        response = requests.get(url, headers=self.get_headers(), verify=False)
        response.raise_for_status()
        return response.json()

    # Helper functions
    def get_services_for_processes(self, processes, from_ts, to_ts):
        # map the process and their services
        processes_services = []
        for process in processes:
            process_id = process['entityId']
            process_services = self.get_services_by_process_id(process_id, from_ts, to_ts)

            services = []
            for service in process_services['entities']:
                services.append(service)
            
            json = {
                'processId': process['entityId'],
                'processName': process['displayName'],
                'services': services
            }
            processes_services.append(json)
        return processes_services
    
    def get_metrics_selector(self, metric_group, metrics_list):
        metrics_selector = metric_group + '.(' + ','.join(metrics_list) + ')'
        return metrics_selector
    
    def filter_allprocess(self, all_process, host):
        filtered_process = []
        for process in all_process['entities']:
            if process['displayName'] in host['process']:
                filtered_process.append(process)
        return filtered_process

















