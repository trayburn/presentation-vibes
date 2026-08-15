using Microsoft.AspNetCore.Http.HttpResults;
using Atlas.Domain;
using Atlas.Services;
using Atlas.Validation;

namespace Atlas.Api;

public static class TaskEndpoints
{
    public static IServiceCollection AddTaskServices(this IServiceCollection services)
    {
        services.AddScoped<ITaskService, TaskService>();
        services.AddScoped<ITaskRepository, TaskRepository>();
        services.AddValidatorsFromAssemblyContaining<TaskValidator>();
        return services;
    }

    public static IEndpointRouteBuilder MapTaskEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/tasks").RequireAuthorization();

        group.MapGet("/", GetTasks);
        group.MapGet("/{id:guid}", GetTaskById);
        group.MapPost("/", CreateTask);
        group.MapPut("/{id:guid}", UpdateTask);
        group.MapDelete("/{id:guid}", DeleteTask);

        return app;
    }

    private static async Task<Results<Ok<List<AtlasTask>>, ProblemHttpResult>> GetTasks(
        ITaskService service, TaskStatus? status = null, string? assigneeId = null)
    {
        var result = await service.GetAllTasksAsync(status, assigneeId);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value)
            : TypedResults.Problem(detail: result.Error, statusCode: 500);
    }

    private static async Task<Results<Ok<AtlasTask>, ProblemHttpResult>> GetTaskById(
        ITaskService service, Guid id)
    {
        var result = await service.GetTaskByIdAsync(id);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value)
            : TypedResults.Problem(detail: result.Error, statusCode: 404, title: "Not Found");
    }

    private static async Task<Results<Created<AtlasTask>, ProblemHttpResult>> CreateTask(
        ITaskService service, TaskCreateRequest request)
    {
        var result = await service.CreateTaskAsync(request.Title, request.Description, request.AssigneeId, request.DueDate);
        return result.IsSuccess
            ? TypedResults.Created($"/api/tasks/{result.Value!.Id}", result.Value)
            : TypedResults.Problem(detail: result.Error, statusCode: 400, title: "Validation Error");
    }

    private static async Task<Results<Ok<AtlasTask>, ProblemHttpResult>> UpdateTask(
        ITaskService service, Guid id, TaskUpdateRequest request)
    {
        var result = await service.UpdateTaskStatusAsync(id, request.Status, request.AssigneeId);
        return result.IsSuccess
            ? TypedResults.Ok(result.Value)
            : TypedResults.Problem(detail: result.Error, statusCode: 400, title: "Validation Error");
    }

    private static async Task<Results<NoContent, ProblemHttpResult>> DeleteTask(
        ITaskService service, Guid id)
    {
        var result = await service.DeleteTaskAsync(id);
        return result.IsSuccess
            ? TypedResults.NoContent()
            : TypedResults.Problem(detail: result.Error, statusCode: 404, title: "Not Found");
    }
}

public record TaskCreateRequest(string Title, string? Description, string? AssigneeId, DateTimeOffset? DueDate);
public record TaskUpdateRequest(TaskStatus Status, string? AssigneeId);