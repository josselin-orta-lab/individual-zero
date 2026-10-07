# I0 modules

This directory contains cognitive mechanisms developed as part of Individual Zero.

## Possible future contents

Examples may include mechanisms related to:

- memory;
- learning;
- regulation;
- motivation;
- action selection;
- perception;
- self-modeling;
- prediction.

These are examples, not a mandated folder structure.

## Do not mirror research axes automatically

Research axes organize questions.

Modules organize implementation.

One module may support several research axes, and one axis may involve several modules.

Create source boundaries because they improve implementation clarity, experimentation, or substitution.

## Reference vs experimental code

Code can begin as an experimental prototype.

It becomes reference I0 code only when the project has enough evidence to integrate it.

Do not treat presence in `src/i0/modules/` as scientific validation by itself.

## Example

A new consolidation policy may be prototyped for one EXP.

If experiments support it, the policy can later become part of the I0 reference module set.

If it fails, its evidence remains valuable even if the prototype is never integrated.
