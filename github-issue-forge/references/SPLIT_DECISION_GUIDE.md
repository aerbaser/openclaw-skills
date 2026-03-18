
# Split Decision Guide

Keep the issue atomic by default.

## Split into multiple issues when

### 1. Discovery is real work
If someone must investigate architecture, measure impact, or choose among designs before implementation begins, create a discovery issue or spike.

### 2. Migration is separable
If rollout, compatibility handling, or data migration can merge later, split it.

### 3. Cleanup is tempting but optional
If the task invites broad cleanup of adjacent files, keep the primary issue narrow and create a follow-up issue for cleanup.

### 4. Verification surface differs
If part of the work is UI, another part is backend, and validation commands or reviewers differ, split it.

## Do not split just because

- there are multiple files,
- the change touches tests and production code,
- the implementation takes more than one commit.

## Rule of thumb

One issue should correspond to one mergeable outcome with one coherent definition of done.
