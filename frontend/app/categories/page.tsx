import { CategoriesPanel } from "@/components/CategoriesPanel";
import { api } from "@/lib/api";

export default async function CategoriesPage() {
  const [categories, progress] = await Promise.all([
    api.getCategories(),
    api.getBudgetProgress(),
  ]);

  return <CategoriesPanel categories={categories} progress={progress} />;
}
