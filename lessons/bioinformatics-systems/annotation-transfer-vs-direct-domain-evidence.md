# Annotation transfer versus direct domain evidence

## The distinction

An annotation transferred through eggNOG and a domain match produced by a
direct Pfam scan may mention the same Pfam family, but they have different
evidence paths and must not be treated as interchangeable observations.

## eggNOG annotation transfer

For a query protein `Q`, the simplified causal chain is:

```text
Q sequence
  -> similarity search against eggNOG proteins
  -> selection of a seed match
  -> orthology assignment using eggNOG's precomputed evolutionary context
  -> transfer of eligible annotations from selected orthologs or groups
  -> predicted annotations for Q
```

The similarity search directly establishes a sequence match. Orthology
assignment then places the query into a more specific evolutionary context.
The final functional labels remain inferred annotations: they are transferred
through that relationship rather than directly measured on the query protein.

An eggNOG `seed_ortholog` is therefore matching evidence used in the inference
chain. It is not the query protein's identity and is not itself a directly
measured functional fact.

An eggNOG `PFAMs` value is auxiliary transferred evidence within the eggNOG
result. It can support the proposition that the query is associated with those
families, but it does not prove that the query was directly scanned against the
corresponding Pfam profile HMMs.

## Direct Pfam scanning

The simplified direct-scan chain is:

```text
Q sequence regions
  -> comparison with Pfam profile HMMs
  -> scored domain matches
  -> match coordinates, scores, E-values, and family identities
```

A standard Pfam profile HMM is a statistical model of aligned amino-acid
sequences. It estimates residue preferences and insertion/deletion behavior at
successive alignment positions. It is not a three-dimensional structural model
and does not contain atomic `x`, `y`, and `z` coordinates.

The model is normally estimated from a curated multiple sequence alignment of
family members. Protein structures may help scientists understand or curate a
family, but HMMER's standard sequence-to-profile calculation does not compare
the query against protein coordinates.

## Why SeqEvi keeps them separate

The evidence paths, semantics, and row grains differ:

| Property | eggNOG `PFAMs` | Direct Pfam evidence |
| --- | --- | --- |
| Immediate basis | Orthology/annotation-transfer chain | Query-to-profile calculation |
| Meaning | Predicted Pfam association | Scored domain match |
| Region coordinates | Not the authoritative direct-scan evidence | Native part of a domain match |
| SeqEvi authority | Auxiliary eggNOG evidence | `interpro-pfam` domain evidence |

One protein may have one eggNOG primary annotation row and multiple direct Pfam
domain-match rows. SeqEvi preserves both adapter-native row grains and does not
silently merge transferred `PFAMs` with direct domain evidence.

## Engine, tool, and adapter boundary

```text
DIAMOND
  -> sequence-search engine

eggNOG-mapper
  -> annotation tool that interprets search and orthology context

SeqEvi eggnog adapter
  -> identity, invocation, validation, normalization, and hit/no-hit boundary
```

The adapter is not the external runtime. In the complete evidence identity,
`AdapterContractVersion` identifies the adapter's interpretation and schema
contract, while `ToolRuntimeDigest` identifies the immutable external runtime.
Changing only the resolved eggNOG-mapper execution environment changes the
runtime coordinate; it does not inherently change the adapter contract.
