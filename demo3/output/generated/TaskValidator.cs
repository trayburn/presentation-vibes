using FluentValidation;
using Atlas.Domain;

namespace Atlas.Validation;

public class TaskValidator : AbstractValidator<AtlasTask>
{
    public TaskValidator()
    {
        RuleFor(t => t.Title)
            .NotEmpty().WithMessage("Title is required")
            .MaximumLength(200).WithMessage("Title must not exceed 200 characters");

        RuleFor(t => t.Status)
            .IsInEnum().WithMessage("Invalid task status");

        RuleFor(t => t.AssigneeId)
            .NotEmpty().When(t => t.Status == TaskStatus.Done)
            .WithMessage("Assignee is required when task status is Done");
    }
}