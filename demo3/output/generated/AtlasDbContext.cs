using Microsoft.EntityFrameworkCore;
using Atlas.Domain;

namespace Atlas.Data;

public class AtlasDbContext : DbContext
{
    public AtlasDbContext(DbContextOptions<AtlasDbContext> options) : base(options) { }

    public DbSet<AtlasTask> Tasks => Set<AtlasTask>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<AtlasTask>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Title).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Description);
            entity.Property(e => e.Status).HasConversion<string>();
            entity.Property(e => e.AssigneeId);
            entity.Property(e => e.DueDate);
            entity.Property(e => e.CreatedAt).IsRequired();
            entity.Property(e => e.UpdatedAt).IsRequired();
        });
    }
}