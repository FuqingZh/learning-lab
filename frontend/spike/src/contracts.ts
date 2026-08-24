export type Relation =
  | "prerequisites"
  | "enables"
  | "contrasts_with"
  | "related";

export interface Source {
  url: string;
  title?: string;
  publisher?: string;
  role?: string;
}
export interface Node {
  id: string;
  title: string;
  summary: string;
  relationships: Partial<Record<Relation, string[]>>;
  sources: Source[];
}
export interface Fixture {
  schema_version: 1;
  name: string;
  nodes: Node[];
}
