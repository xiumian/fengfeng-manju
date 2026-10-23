# Prompt Templates

## Video template

```text
[Duration] [style] video shot.

Character A, [stable visual anchor], starts at [screen/set position].
[Prop] remains [exact position/state]. A's baseline is [visible baseline].

When [specific trigger] occurs, [first involuntary cue]. After [brief pause],
[gaze/eyelid change], while [head/body constraint]. Then [mouth/jaw/breath cue].
A attempts to [mask or control the reaction] and ends [readable end state].

Performance is [trace/restrained/clear/overt], natural, and sequential rather
than a held expression.

Camera: [shot size], [angle], [lens feel], [one movement or static]. Keep
[eyes/mouth/prop/composition anchor] readable. [Confirmed light source].
Keep [identity, position, prop, eyeline, light, and set continuity].

No [targeted performance failures]. No [video continuity failures].
```

## Still-image template

```text
[Style] still image of Character A at [location]. Capture the instant after
[trigger] but before [next action]. A shows [2-4 coordinated visible cues].
The expression is restrained and transitional, not a fixed emotional pose.
[Prop and body state]. [Shot size, angle, lens feel, composition, lighting].
No frozen neutral face, no exaggerated expression, no facial asymmetry beyond
the specified subtle cue, no identity drift, no prop distortion.
```

## Worked video example

Source:

```text
秦剑师在祭坛前微阖双目，看似打坐，实则昏睡。桃木剑横放在盘坐的
双腿上。听到竹林里的声音，他微睁双目，瞟向身后的声音来处。
```

Emotion beat:

```text
baseline: disguised meditation, actual sleepiness
trigger: sound from the bamboo grove behind him
leak: eyelid twitch and interrupted breath
controlled response: eyes move before the head; body remains seated
end state: sleepiness becomes restrained alertness
```

Prompt:

```text
A 6-second realistic historical-fantasy cinematic shot. Character A, Qin the
swordsman, sits cross-legged at the center before an old altar. A peach-wood
sword lies horizontally across both thighs and remains completely still. His
eyes are nearly closed as if meditating, but his slightly lowered head, loose
jaw, relaxed shoulders, and slow breathing reveal that he has fallen asleep.

A faint sound comes from the bamboo grove behind him. His eyelids twitch once
and his breath pauses. He opens his eyes only to a narrow slit, still carrying
the dullness of sleep. Without moving his torso or head, his eyes shift first
toward the sound source behind him. After a brief pause, his jaw tightens
slightly and his head turns only a few degrees as he listens. He ends seated,
quiet, and restrainedly alert.

Eye-level medium close-up with a 50mm lens feel. The camera performs one slow
dolly-in while keeping his eyes and the sword readable. Natural ambient light
filters through bamboo leaves; treat this lighting as an assumption unless an
asset establishes it. No cuts inside the shot.

No sudden wide-eyed reaction, no sharp head snap, no exaggerated fear, no
constant frozen expression, no mechanical blinking, no standing, no drawing
the sword, no sword movement, no facial morphing, no identity drift, no extra
people, no background flicker, no orbit, and no handheld shake.
```
