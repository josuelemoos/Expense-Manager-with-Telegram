import { PlanningPanel } from "@/components/PlanningPanel";
import { api } from "@/lib/api";

export default async function PlanningPage() {
  const [progress, allocations, categories] = await Promise.all([
    api.getPlanProgress(),
    api.getAllocations(),
    api.getCategories(),
  ]);

  return (
    <PlanningPanel
      progress={progress}
      allocations={allocations}
      categories={categories}
    />
  );
}
