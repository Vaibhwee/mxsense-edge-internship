import { redirect } from "next/navigation";


export default async function LegacyModuleRedirect({ params }) {
  const { slug } = await params;
  redirect(`/dashboard/modules/${slug}`);
}
