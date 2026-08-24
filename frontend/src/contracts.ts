export type EdgeType =
  | "prerequisites"
  | "enables"
  | "contrasts_with"
  | "related";
export type MasteryStatus = "mastered" | "developing" | "not-started" | string;

export interface Source {
  url: string;
  title?: string;
  publisher?: string;
  role?: string;
  kind?: string;
}
export interface Terminology {
  preferred_english_term: string;
  checked_on: string;
  sources: Source[];
}
export interface Concept {
  id: string;
  title: string;
  summary: string;
  kind: string;
  path: string;
  tracks: string[];
  lessons: string[];
  records: string[];
  case_labs: string[];
  mastery: { status: MasteryStatus; effective_record?: string | null };
  relationships: Partial<Record<EdgeType, string[]>>;
  extensions?: { terminology?: Terminology };
}
export interface Graph {
  schema_version: 1;
  nodes: Concept[];
  edges: Edge[];
  tracks: string[];
  case_labs: CaseLab[];
}
export interface Edge {
  source: string;
  target: string;
  type: EdgeType;
}
export interface CaseLab {
  id: string;
  title: string;
  path: string;
  direct_concepts: string[];
}
export interface LearningConcept {
  id: string;
  capability_state: string;
  next_review: string | null;
  latest_outcome: string | null;
}
export interface LearningState {
  schema_version: 1;
  concepts: LearningConcept[];
  resume?: { next: string; summary?: string } | null;
}
export interface Milestone {
  id: string;
  year: number;
  month?: number | null;
  day?: number | null;
  kind: string;
  claim: string;
  actors?: string[];
  sources?: Source[];
}
export interface Dossier {
  id: string;
  title: string;
  summary: string;
  path: string;
  tracks: string[];
  concepts: string[];
  lessons: string[];
  milestones: Milestone[];
}
export interface History {
  schema_version: 1;
  dossiers: Dossier[];
}
export type EvidenceNodeKind = "concept" | "dossier" | "milestone" | "source";
export type EvidenceEdgeKind = "about" | "cites_as_evidence" | "contained_in";
export interface EvidenceDate {
  year: number;
  month?: number | null;
  day?: number | null;
}
export interface EvidenceNode {
  id: string;
  kind: EvidenceNodeKind;
  title?: string;
  path?: string;
  concept_id?: string;
  dossier_id?: string;
  milestone_id?: string;
  milestone_kind?: string;
  claim?: string;
  actors?: string[];
  date?: EvidenceDate;
  boundaries?: string[];
  summary?: string;
  publisher?: string;
  source_kind?: string;
  canonical_url?: string;
}
export interface EvidenceEdge {
  kind: EvidenceEdgeKind;
  from: string;
  to: string;
  role?: string;
  locator?: string;
  url?: string;
}
export interface EvidenceGraph {
  schema_version: 1;
  nodes: EvidenceNode[];
  edges: EvidenceEdge[];
}
export interface FrontendData {
  graph: Graph;
  learningState: LearningState;
  history: History;
  evidenceGraph: EvidenceGraph;
}
export const edgeTypes: readonly EdgeType[] = [
  "prerequisites",
  "enables",
  "contrasts_with",
  "related",
];
