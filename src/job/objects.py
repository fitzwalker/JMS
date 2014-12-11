import xml.etree.ElementTree as ET
import os, socket
from Utilities import *

#####
# Workflow objects
#####

class Status:

    Created = 1
    Queued = 2
    Running = 3
    Completed_Successfully = 4
    Awaiting_User_Input = 5
    Stopped = 6
    Failed = 7

class ParameterType:

    Text = 1
    Number = 2
    Boolean = 3
    Options = 4
    File = 5
    Previous_Parameter = 6
    Complex_Object = 7
    Related_Object = 8


class ResultType:

    Templates = 1
    Alignment = 2
    PDB_File = 3
    Model_Validation_Scores = 4


class Editor:

    Default = 1
    Protein_Visualizer = 2
    Template_Selector = 3


class AccessRights:

    Owner = 1
    Admin = 2
    View_And_Comment = 3
    View = 4
    No_Access = 5


class DependencyCondition:

    Success = 1
    Failed = 2
    Completed = 3
    Exit_Code = 4
    
    @staticmethod
    def GetDependencyType(software, condition):
        if software == "torque":
            return {
                DependencyCondition.Success: "afterok",
                DependencyCondition.Failed: "afternotok",
                DependencyCondition.Completed: "afterany"
            }.get(condition, None)
        else:
            return None
    
    @staticmethod
    def GetArrayDependencyType(software, condition):
        if software == "torque":
            return {
                DependencyCondition.Success: "afterokarray",
                DependencyCondition.Failed: "afternotok",
                DependencyCondition.Completed: "afteranyarray"
            }.get(condition, None)
        else:
            return None
    
    
class JobStageInput:

    def __init__(self, stage_id, parameters, requires_edit):
        self.stage_id = stage_id
        self.parameters = parameters
        self.requires_edit = requires_edit


#####
# Dashboard objects
#####

class Node:
    
    def __init__(self, name, state, num_cores, busy_cores, free_cores, properties):
        self.name = name
        self.state = state
        self.num_cores = num_cores
        self.busy_cores = busy_cores
        self.free_cores = free_cores
        self.properties = properties
        self.jobs = []


class Job:
    
    def __init__(self, job_id, cores):
        self.job_id = job_id
        self.cores = cores

class JobDetail():
    ClusterJobID = ""
    JobName = ""
    JobOwner = ""
    
    MemoryRequested = ""
    NodesAvailable = ""
    NodesRequested = ""
    WalltimeRequested = ""
    
    CPUTimeUsed = ""
    MemoryUsed = ""
    VirtualMemoryUsed = ""
    WalltimeUsed = ""
    
    State = ""
    Queue = ""
    Server = ""
    ExecutionHost = ""
    SubmitArgs = ""
    SubmitHost = ""
    OutputPath = ""
    ErrorPath = ""
    Priority = ""
    
    CreatedTime = ""
    TimeEnteredQueue = ""
    EligibleTime = ""
    LastModified = ""
    StartTime = ""
    CompletionTime = ""
    TotalRuntime = ""
    
    VariableList = ""
    
    Comment = ""
    ExitStatus = ""    
    
    OutputStream = "Output stream not available"
    ErrorStream = "Error stream not available"
    
    @staticmethod
    def ParseClusterJobs(jobs_string):
        
        jobs = []
        
        jobs_arr = jobs_string.split("\n\n")
        
        for job_string in jobs_arr:
            job = JobDetail.ParseClusterJob(job_string)
            
            if job:
                jobs.append(job)
        
        return jobs        
    
    
    @staticmethod
    def ParseClusterJob(job_string):
        job = JobDetail()
        
        job_arr = job_string.split('\n')
        if len(job_arr) > 5:
            i = 0
            while i < len(job_arr):
                line = job_arr[i].rstrip()
        
                if len(line) > 0 and line[0] == 'J':
                    job.ClusterJobID = line.split(':')[1].strip()
                else:
                    entry = line[4:].split(" = ")
                
                    if entry[0] == "Job_Name":
                        job.JobName = entry[1]
                    elif entry[0] == "Job_Owner":
                        job.JobOwner = entry[1]
                    elif entry[0] == "resources_used.cput":
                        job.CPUTimeUsed = entry[1]
                    elif entry[0] == "resources_used.mem":
                        job.MemoryUsed = entry[1]
                    elif entry[0] == "resources_used.vmem":
                        job.VirtualMemoryUsed = entry[1]
                    elif entry[0] == "resources_used.walltime":
                        job.WalltimeUsed = entry[1]
                    elif entry[0] == "job_state":
                        job.State = entry[1]
                    elif entry[0] == "queue":
                        job.Queue = entry[1]
                    elif entry[0] == "server":
                        job.Server = entry[1]
                    elif entry[0] == "ctime":
                        job.CreatedTime = entry[1]
                    elif entry[0] == "Error_Path":
                        job.ErrorPath = entry[1]
                    elif entry[0] == "exec_host":
                        job.ExecutionHost = entry[1]
                    elif entry[0] == "mtime":
                        job.LastModified = entry[1]
                    elif entry[0] == "Output_Path":
                        job.OutputPath = entry[1]
                    elif entry[0] == "Priority":
                        job.Priority = entry[1]
                    elif entry[0] == "qtime":
                        job.TimeEnteredQueue = entry[1]
                    elif entry[0] == "Resource_List.mem":
                        job.MemoryRequested = entry[1]
                    elif entry[0] == "Resource_List.nodect":
                        job.NodesAvailable = entry[1]
                    elif entry[0] == "Resource_List.nodes":
                        job.NodesRequested = entry[1]
                    elif entry[0] == "Resource_List.walltime":
                        job.WalltimeRequested = entry[1]
                    elif entry[0] == "Variable_List":
                        job.VariableList = entry[1]    
                    
                        i += 1
                        line = job_arr[i].rstrip()
                        while line[0] == "\t":
                            job.VariableList += line.strip()
                        
                            i += 1
                            line = job_arr[i].rstrip()
                        continue                
                    elif entry[0] == "comment":
                        job.Comment = entry[1]
                    elif entry[0] == "etime":
                        job.EligibleTime = entry[1]
                    elif entry[0] == "exit_status":
                        job.ExitStatus = entry[1]
                    elif entry[0] == "submit_args":
                        job.SubmitArgs = entry[1]
                    
                        i += 1
                        line = job_arr[i].rstrip()
                        while line[0] == "\t":
                            job.SubmitArgs += line.strip()
                        
                            i += 1
                            line = job_arr[i].rstrip()
                        continue
                    elif entry[0] == "start_time":
                        job.StartTime = entry[1]
                    elif entry[0] == "comp_time":
                        job.CompletionTime = entry[1]
                    elif entry[0] == "total_runtime":
                        job.TotalRuntime = entry[1]
                    elif entry[0] == "submit_host":
                        job.SubmitHost = entry[1]
                
                i += 1
                
            return job
        else:
            return False
        

class QueueItem:
    
    def __init__(self, job_id, username, job_name, nodes, cores, state, time, queue):
        self.job_id = job_id
        self.username = username
        self.job_name = job_name
        self.nodes = nodes
        self.cores = cores
        self.state = state
        self.time = time
        self.queue = queue


class DiskUsage:

    def __init__(self, disk_size, available_space, used_space):
        self.disk_size = disk_size
        self.available_space = available_space
        self.used_space = used_space
                 

class Dashboard:

    def __init__(self, username, password):
        process = UserProcess(username, password)
        
        self.nodes = self.GetNodes(process)
        self.queue = self.GetQueue(process)        
        self.disk = self.GetDiskUsage(process, "/obiwanNFS")
        
        process.close()
                            
        
    def GetDiskUsage(self, process, path):
        out = process.run_command("df -h %s" % path)
        
        lines = out.split('\n')
        
        index = lines[0].index("Size")
        size = lines[1][index:index+5].strip()        
        used = lines[1][index+5:index+11].strip()
        available = lines[1][index+11:index+17].strip()
        
        return DiskUsage(size, available, used)
        
    
    def GetNodes(self, process):
        nodes = []
        
        out = process.run_command("qnodes -x")
        
        root = ET.fromstring(out)
        
        for node in root.iter('Node'):
            name = node.find('name').text
            state = node.find('state').text
            num_cores = int(node.find('np').text)
            properties = node.find('state').text
            busy_cores = 0;            
            
            job_dict = dict()
            
            jobs = node.find('jobs')
            if jobs is not None:            
                jobs = jobs.text
                job_cores = jobs.split(',')            
            
                for core in job_cores:
                    job_core = core.split('/')
                
                    key = job_core[1]
                    
                    core_range = job_core[0].split("-")
                    if len(core_range) > 1:
                        for i in range(int(core_range[0]), int(core_range[1])+1):                            
                            busy_cores += 1
                            if key in job_dict:
                                job_dict[key].append(i)
                            else:
                                job_dict[key] = [i]
                    else:
                        busy_cores += 1
                        if key in job_dict:
                            job_dict[key].append(job_core[0])
                        else:
                            job_dict[key] = [job_core[0]]
            
            free_cores = num_cores - busy_cores
            
            n = Node(name, state, num_cores, busy_cores, free_cores, properties)
            
            for k in job_dict:
                j = Job(k, job_dict[k])                
                n.jobs.append(j)
            
            nodes.append(n)
        
        return nodes
    
    def GetQueue(self, process):
        queue = []
        
        out = process.run_command("qstat -a")
        
        lines = out.split('\n')
        
        count = 0
        for line in lines:
            if count > 4 and len(line) > 0:
                job_id = line[0:23].strip()
                username = line[24:35].strip()
                job_name = line[45:61].strip()
                nodes = int(line[69:74].strip())
                cores = int(line[75:81].strip())
                state = line[99]
                time = line[101:].strip()
                q = line[36:44].strip()
                
                queue.append(QueueItem(job_id, username, job_name, nodes, cores, state, time, q))            
            
            count += 1            
        
        return queue

####
# Settings objects    
####

class TorqueServer:
    
    def __init__(self, ServerName="", KeepCompleted=None, JobStatRate=None, SchedularIteration=None, NodeCheckRate=None, TCPTimeout=None, QueryOtherJobs=None, MOMJobSync=None, MoabArrayCompatible=None, Scheduling=None, ServerAdmins=[], Queues=[]):
        self.ServerName = ServerName
        self.KeepCompleted = KeepCompleted
        self.JobStatRate = JobStatRate
        self.SchedularIteration = SchedularIteration
        self.NodeCheckRate = NodeCheckRate
        self.TCPTimeout = TCPTimeout
        self.QueryOtherJobs = QueryOtherJobs
        self.MOMJobSync = MOMJobSync
        self.MoabArrayCompatible = MoabArrayCompatible
        self.Scheduling = Scheduling
        self.ServerAdministrators = ServerAdmins
        self.Queues = Queues
        
        
class ServerAdministrator:

    def __init__(self, Username=None, Host=None, Manager=None, Operator=None):
        self.Username = Username
        self.Host = Host
        self.Manager = Manager
        self.Operator = Operator
    
    
class Queue:

    def __init__(self, QueueName=None, Type=None, Enabled=None, Started=None, MaxQueable=None, MaxRun=None, MaxUserQueable=None, MaxUserRun=None, MaxNodes=None, DefaultNodes=None, MaxCPUs=None, DefaultCPUs=None, MaxMemory=None, DefaultMemory=None, MaxWalltime=None, DefaultWalltime=None, DefaultQueue=False):
        self.QueueName = QueueName
        self.Type = Type
        self.Enabled = Enabled
        self.Started = Started
        self.MaxQueable = MaxQueable
        self.MaxRun = MaxRun
        self.MaxUserQueable = MaxUserQueable
        self.MaxUserRun = MaxUserRun
        self.MaxNodes = MaxNodes
        self.DefaultNodes = DefaultNodes
        self.MaxCPUs = MaxCPUs
        self.DefaultCPUs = DefaultCPUs
        self.MaxMemory = MaxMemory
        self.DefaultMemory = DefaultMemory
        self.MaxWalltime = MaxWalltime
        self.DefaultWalltime = DefaultWalltime
        self.DefaultQueue = DefaultQueue


class Client:

    def __init__(self, NodeName=None, State=None, NumProcessors=None, Properties=None):
        self.NodeName = NodeName
        self.State = State
        self.NumProcessors = NumProcessors
        self.Properties = Properties
        