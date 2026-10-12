import type { Metadata } from "next";
import AircraftWorkbench from "@/components/aircraft-workbench";
export const metadata: Metadata = {
  title: "MiG-29K & Mil Mi-24 · Paper Craft",
  description:
    "Build 1:400 paper aircraft with a four-sheet A4 print pack and illustrated assembly guides.",
};
export default function AircraftPage() {
  return <AircraftWorkbench />;
}
