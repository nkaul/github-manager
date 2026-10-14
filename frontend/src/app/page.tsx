import Preflight from "@/components/Preflight";
import WorkspaceApp from "@/components/WorkspaceApp";

export default function Page() {
  return process.env.GHM_UI === "preflight" ? <Preflight /> : <WorkspaceApp />;
}
