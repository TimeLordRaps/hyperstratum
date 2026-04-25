# Graph-Prefix Grammar

This document defines graph terms compositionally.

The goal is to prevent `self`, `mira`, and `recursive` from collapsing into one blurred concept.

## Base term: graph

```txt
graph = structured representation of nodes and connections
```

A graph represents relation-structure. In Hyperstratum, graph terms may represent base-level relations, meta-level relations, recursive structures, self-relations, reflective appearances, or combinations of these.

## Prefix: recursive-

```txt
recursive- = base/meta/whole-form recursion
```

A recursive-graph represents recursive form-structure.

```txt
recursive-graph = graph representation of recursive form-structure, where nodes and connections may contain or refer to base/meta/meta-meta levels.
```

`R-graph` may be used as shorthand, but `recursive-graph` is the canonical term.

## Prefix: self-

```txt
self- = subject/object self-relation
```

A self-graph represents a subject in relation to itself.

```txt
self-graph = graph whose subject is represented in relation to itself.
```

A self-graph does not necessarily require reflection, self-awareness, or recursion. It only requires that the represented object and representing subject are in a self-relation.

Examples:

```txt
A system state diagram referring to its own prior state.
A person's map of their values.
A model tracking its own outputs.
```

## Prefix: mira-

```txt
mira- = reflective appearance from an interpretive position
```

A mira-graph represents how a form appears from an interpretive position.

```txt
mira-graph = reflective graph representing how a form appears from an interpretive position.
```

A mira-graph does not have to be self-directed. It can represent how one agent, society, institution, model, or frame reflects another object.

Examples:

```txt
A society's representation of a person.
A reader's interpretation of a text.
A model's representation of a prompt.
```

## Composition rule

Prefixes compose left-to-right as modifiers of the graph type.

```txt
self-mira-recursive-graph
```

Means:

```txt
A recursive graph by which a subject reflectively represents itself to itself across base/meta/whole-form levels.
```

Breakdown:

```txt
recursive-graph = graph of recursive form-structure
mira-recursive-graph = reflective graph of recursive form-structure from an interpretive position
self-mira-recursive-graph = reflective recursive graph where the subject represents itself to itself
```

## Distinctions

### Self-graph vs mira-graph

```txt
self-graph = relation of a subject to itself
mira-graph = reflective representation from an interpretive position
```

A self-graph can be non-reflective. A mira-graph can be non-self-directed.

### Self-graph vs recursive-graph

```txt
self-graph = about self-relation
recursive-graph = about base/meta/whole-form recursion
```

A self-graph can be flat. A recursive-graph can be about a non-self object.

### Mira-graph vs recursive-graph

```txt
mira-graph = about reflective appearance
recursive-graph = about recursive form-depth
```

A mira-graph can reflect a flat object. A recursive-graph can represent recursive structure without specifying a reflective viewpoint.

## Identity application

For personhood, the clean distinction is:

```txt
self-mira-recursive-graph != social-mira-graph
```

A person's core identity is closer to a self-mira-recursive-graph: a recursive reflective graph by which the person-hypernode represents itself to itself.

Social reception is a social-mira-graph: an external reflective graph by which a society receives, labels, interprets, or misrepresents a person-hypernode.

Reception is not identity. Reception is an attempted representation of identity by an outside system.
