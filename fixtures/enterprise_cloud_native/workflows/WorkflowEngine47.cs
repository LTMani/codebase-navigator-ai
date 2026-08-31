namespace Navigator.Enterprise.Workflows.Engine47;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public enum WorkflowExecutionState47
{
    Pending,
    Running,
    Completed,
    Failed,
    Suspended
}

public class EnterpriseWorkflowEngine47
{
    public record WorkflowJob(Guid JobId, string WorkflowName, WorkflowExecutionState47 State, DateTime StartedAt);

    private readonly ConcurrentDictionary<Guid, WorkflowJob> _activeJobs = new();

    public Task<WorkflowJob> StartWorkflowAsync(string workflowName)
    {
        var job = new WorkflowJob(Guid.NewGuid(), workflowName, WorkflowExecutionState47.Running, DateTime.UtcNow);
        _activeJobs[job.JobId] = job;
        return Task.FromResult(job);
    }

    public Task<bool> CompleteWorkflowAsync(Guid jobId)
    {
        if (_activeJobs.TryGetValue(jobId, out var job))
        {
            var completed = job with {{ State = WorkflowExecutionState47.Completed }};
            _activeJobs[jobId] = completed;
            return Task.FromResult(true);
        }
        return Task.FromResult(false);
    }
}
