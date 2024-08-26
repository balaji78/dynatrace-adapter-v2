import json
import logging as logger
from dynatraceapi import DynatraceAPI

class DynatraceDataCollector:

    def __init__(self):
        datacollector = open('./datacollector.json')
        dc = json.load(datacollector)
        self.base_url = dc['base_url']
        self.api_token = dc['api-token']
        self.applications = dc['applications']

    def get_data(self, start_time, end_time, resolution = '1m'):        
        try:
            dt_api = DynatraceAPI(self.base_url, self.api_token)

            for application in self.applications:
                for host in application['host']:
                    for key in host['metrics']:

                        host_id = host['host-id']
                        all_processes = {}
                        filtered_processes = {}
                        processes_services = {}

                        #get all processes and services for the host if those metrics are configured
                        if("builtin:tech" in host['metrics'] or "builtin:tech.generic" in host['metrics']):
                            #get all the process running inside the host
                            all_processes = dt_api.get_processes_for_host(host_id, start_time, end_time)

                            #filter only the mentioned processes
                            filtered_processes = dt_api.filter_allprocess(all_processes, host)

                            #get all services for the filtered processes
                            if("builtin:service" in host['metrics'] or "calc:service" in host['metrics']):
                                #get services of each process
                                processes_services = dt_api.get_services_for_processes(filtered_processes, start_time, end_time)
                                #print(processes_services)

                        #check if metrics are configured first
                        if(len(host['metrics'][f'{key}']) > 0):

                            metrics_selector = dt_api.get_metrics_selector(key, host['metrics'][f'{key}'])

                            #get the host metrics
                            if(key == "builtin:host"):
                                metrics = dt_api.get_metrics(host_id, metrics_selector, start_time, end_time, resolution)
                                print(metrics)
                            #get the process / service metrics
                            else:
                                match key:
                                    case "builtin:tech" | "builtin:tech.generic":
                                        for process in filtered_processes:
                                            process_id = process['entityId']
                                            metrics = dt_api.get_metrics(process_id, metrics_selector, start_time, end_time, resolution)
                                            print(metrics)
                                    case "builtin:service" | "calc:service":
                                        for process in processes_services:
                                            process_id = process['processId']
                                            process_name = process['processName']
                                            for service in process['services']:
                                                service_id = service['entityId']
                                                metrics = dt_api.get_metrics(service_id, metrics_selector, start_time, end_time, resolution)
                                                print(metrics) 
        except Exception as e:
            logger.error(e)

#dc = DataCollector()
