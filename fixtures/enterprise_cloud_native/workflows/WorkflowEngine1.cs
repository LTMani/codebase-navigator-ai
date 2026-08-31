namespace Navigator.Enterprise.Workflows.Engine1;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public enum WorkflowExecutionState1
{
    Pending,
    Running,
    Completed,
    Failed,
    Suspended
}

public class EnterpriseWorkflowEngine1
{
    public record WorkflowJob(Guid JobId, string WorkflowName, WorkflowExecutionState1 State, DateTime StartedAt);

    private readonly ConcurrentDictionary<Guid, WorkflowJob> _activeJobs = new();

    public Task<WorkflowJob> StartWorkflowAsync(string workflowName)
    {
        var job = new WorkflowJob(Guid.NewGuid(), workflowName, WorkflowExecutionState1.Running, DateTime.UtcNow);
        _activeJobs[job.JobId] = job;
        return Task.FromResult(job);
    }

    public Task<bool> CompleteWorkflowAsync(Guid jobId)
    {
        if (_activeJobs.TryGetValue(jobId, out var job))
        {
            var completed = job with {{ State = WorkflowExecutionState1.Completed }};
            _activeJobs[jobId] = completed;
            return Task.FromResult(true);
        }
        return Task.FromResult(false);
    }
}
