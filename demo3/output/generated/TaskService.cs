using Atlas.Domain;

namespace Atlas.Services;

public interface ITaskService
{
    Task<Result<List<AtlasTask>>> GetAllTasksAsync(TaskStatus? status = null, string? assigneeId = null);
    Task<Result<AtlasTask>> GetTaskByIdAsync(Guid id);
    Task<Result<AtlasTask>> CreateTaskAsync(string title, string? description, string? assigneeId, DateTimeOffset? dueDate);
    Task<Result<AtlasTask>> UpdateTaskStatusAsync(Guid id, TaskStatus newStatus, string? assigneeId);
    Task<Result> DeleteTaskAsync(Guid id);
}

public class TaskService : ITaskService
{
    private readonly ITaskRepository _repository;

    public TaskService(ITaskRepository repository)
    {
        _repository = repository;
    }

    public async Task<Result<List<AtlasTask>>> GetAllTasksAsync(TaskStatus? status = null, string? assigneeId = null)
    {
        var tasks = await _repository.GetAllAsync(status, assigneeId);
        return Result<List<AtlasTask>>.Success(tasks);
    }

    public async Task<Result<AtlasTask>> GetTaskByIdAsync(Guid id)
    {
        var task = await _repository.GetByIdAsync(id);
        if (task is null)
            return Result<AtlasTask>.Failure("Task not found");

        return Result<AtlasTask>.Success(task);
    }

    public async Task<Result<AtlasTask>> CreateTaskAsync(string title, string? description, string? assigneeId, DateTimeOffset? dueDate)
    {
        if (string.IsNullOrWhiteSpace(title))
            return Result<AtlasTask>.Failure("Title is required");

        if (title.Length > 200)
            return Result<AtlasTask>.Failure("Title must not exceed 200 characters");

        var task = new AtlasTask
        {
            Id = Guid.NewGuid(),
            Title = title,
            Description = description,
            Status = TaskStatus.Todo,
            AssigneeId = assigneeId,
            DueDate = dueDate,
            CreatedAt = DateTimeOffset.UtcNow,
            UpdatedAt = DateTimeOffset.UtcNow
        };

        await _repository.AddAsync(task);
        return Result<AtlasTask>.Success(task);
    }

    public async Task<Result<AtlasTask>> UpdateTaskStatusAsync(Guid id, TaskStatus newStatus, string? assigneeId)
    {
        var task = await _repository.GetByIdAsync(id);
        if (task is null)
            return Result<AtlasTask>.Failure("Task not found");

        // Business rule: cannot move to Done without an assignee
        if (newStatus == TaskStatus.Done && string.IsNullOrWhiteSpace(task.AssigneeId) && string.IsNullOrWhiteSpace(assigneeId))
            return Result<AtlasTask>.Failure("Cannot move task to Done without an assignee");

        task.Status = newStatus;
        if (!string.IsNullOrWhiteSpace(assigneeId))
            task.AssigneeId = assigneeId;
        task.UpdatedAt = DateTimeOffset.UtcNow;

        await _repository.UpdateAsync(task);
        return Result<AtlasTask>.Success(task);
    }

    public async Task<Result> DeleteTaskAsync(Guid id)
    {
        var task = await _repository.GetByIdAsync(id);
        if (task is null)
            return Result.Failure("Task not found");

        await _repository.DeleteAsync(id);
        return Result.Success();
    }
}