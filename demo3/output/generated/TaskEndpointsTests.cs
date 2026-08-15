using System.Net;
using System.Net.Http.Json;
using Atlas.Domain;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace Atlas.Tests.Integration;

public class TaskEndpointsTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public TaskEndpointsTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GET_Tasks_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/tasks");
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    [Fact]
    public async Task POST_Task_ValidInput_ReturnsCreated()
    {
        var request = new { Title = "Integration Test Task", Description = "Test", AssigneeId = "user1", DueDate = (DateTimeOffset?)null };
        var response = await _client.PostAsJsonAsync("/api/tasks", request);
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }

    [Fact]
    public async Task POST_Task_EmptyTitle_Returns400()
    {
        var request = new { Title = "", Description = (string?)null, AssigneeId = (string?)null, DueDate = (DateTimeOffset?)null };
        var response = await _client.PostAsJsonAsync("/api/tasks", request);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task PUT_Task_DoneWithoutAssignee_Returns400()
    {
        // First create a task without assignee
        var createRequest = new { Title = "Test Task", Description = (string?)null, AssigneeId = (string?)null, DueDate = (DateTimeOffset?)null };
        var createResponse = await _client.PostAsJsonAsync("/api/tasks", createRequest);
        var created = await createResponse.Content.ReadFromJsonAsync<dynamic>();

        // Try to move to Done without assignee
        var updateRequest = new { Status = TaskStatus.Done, AssigneeId = (string?)null };
        var response = await _client.PutAsJsonAsync($"/api/tasks/{created.Id}", updateRequest);
        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
    }

    [Fact]
    public async Task GET_Task_NotFound_Returns404()
    {
        var response = await _client.GetAsync($"/api/tasks/{Guid.NewGuid()}");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }

    [Fact]
    public async Task DELETE_Task_NotFound_Returns404()
    {
        var response = await _client.DeleteAsync($"/api/tasks/{Guid.NewGuid()}");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}