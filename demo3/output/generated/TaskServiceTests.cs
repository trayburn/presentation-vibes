using Atlas.Domain;
using Atlas.Services;
using Xunit;

namespace Atlas.Tests.Unit;

public class TaskServiceTests
{
    private readonly ITaskService _service;
    private readonly Mock<ITaskRepository> _repoMock;

    public TaskServiceTests()
    {
        _repoMock = new Mock<ITaskRepository>();
        _service = new TaskService(_repoMock.Object);
    }

    [Fact]
    public async Task CreateTask_ValidInput_ReturnsSuccess()
    {
        // Arrange
        _repoMock.Setup(r => r.AddAsync(It.IsAny<AtlasTask>()))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _service.CreateTaskAsync("Test Task", "Description", "user1", null);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Equal("Test Task", result.Value!.Title);
    }

    [Fact]
    public async Task CreateTask_EmptyTitle_ReturnsFailure()
    {
        // Act
        var result = await _service.CreateTaskAsync("", null, null, null);

        // Assert
        Assert.True(result.IsFailure);
        Assert.Contains("Title is required", result.Error);
    }

    [Fact]
    public async Task CreateTask_TitleExceeds200Chars_ReturnsFailure()
    {
        // Arrange
        var longTitle = new string('a', 201);

        // Act
        var result = await _service.CreateTaskAsync(longTitle, null, null, null);

        // Assert
        Assert.True(result.IsFailure);
        Assert.Contains("200", result.Error);
    }

    [Fact]
    public async Task UpdateTaskStatus_DoneWithoutAssignee_ReturnsFailure()
    {
        // Arrange
        var task = new AtlasTask { Id = Guid.NewGuid(), Title = "Test", Status = TaskStatus.Todo };
        _repoMock.Setup(r => r.GetByIdAsync(task.Id)).ReturnsAsync(task);

        // Act
        var result = await _service.UpdateTaskStatusAsync(task.Id, TaskStatus.Done, null);

        // Assert
        Assert.True(result.IsFailure);
        Assert.Contains("assignee", result.Error, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task UpdateTaskStatus_DoneWithAssignee_ReturnsSuccess()
    {
        // Arrange
        var task = new AtlasTask { Id = Guid.NewGuid(), Title = "Test", Status = TaskStatus.Todo, AssigneeId = "user1" };
        _repoMock.Setup(r => r.GetByIdAsync(task.Id)).ReturnsAsync(task);

        // Act
        var result = await _service.UpdateTaskStatusAsync(task.Id, TaskStatus.Done, null);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Equal(TaskStatus.Done, result.Value!.Status);
    }

    [Fact]
    public async Task GetTaskById_NotFound_ReturnsFailure()
    {
        // Arrange
        var id = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(id)).ReturnsAsync((AtlasTask?)null);

        // Act
        var result = await _service.GetTaskByIdAsync(id);

        // Assert
        Assert.True(result.IsFailure);
        Assert.Contains("not found", result.Error, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task DeleteTask_NotFound_ReturnsFailure()
    {
        // Arrange
        var id = Guid.NewGuid();
        _repoMock.Setup(r => r.GetByIdAsync(id)).ReturnsAsync((AtlasTask?)null);

        // Act
        var result = await _service.DeleteTaskAsync(id);

        // Assert
        Assert.True(result.IsFailure);
    }
}