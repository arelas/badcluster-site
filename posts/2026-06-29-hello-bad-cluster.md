---
title: Hello, Bad Cluster
date: 2026-06-29
summary: Why we picked this name, and what this site is actually for.
---

A FAT32 filesystem keeps a table of every cluster on a disk. Most entries
just point to the next cluster in a file, or mark one as free. A small
number get a special value instead: `0x0FFFFFF7`. That one means *bad
cluster* - hardware found this spot unreliable, so don't use it. The
filesystem doesn't pretend the cluster works. It just marks it and moves
on.

That's the whole reason for the name. We'd rather ship something small and
honestly-labeled than something polished that quietly hides where it
doesn't work.

## What this site is

A place to put things we build that we think are worth sharing. Right now
that's [PHAT32](/#projects), a Windows tool for formatting drives as FAT32
past the 32&nbsp;GB limit Windows' own formatter won't let you cross. It
won't always be tools, and it won't always be Windows-specific - whatever
we end up making, if it's useful enough to hand to someone else, it ends
up here.

## What this blog is

Notes on what we're actually building, written close to when we build it.
Not a marketing calendar - if there's nothing worth writing about in a
given month, there won't be a post that month.

If you want to reach us about any of it, there's a [contact
form](/contact/) for that.
