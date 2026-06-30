import PageBreadcrumb from "@/components/common/PageBreadCrumb";
import ResidentForm from "@/components/residents/ResidentForm";

export default function NewResidentPage() {
  return (
    <div className="p-4 mx-auto max-w-screen-2xl md:p-6">
      <PageBreadcrumb pageTitle="Nuevo Residente" />
      <div className="rounded-2xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-white/[0.03]">
        <h2 className="mb-6 text-lg font-semibold text-gray-800 dark:text-white">
          Datos del residente
        </h2>
        <ResidentForm />
      </div>
    </div>
  );
}
