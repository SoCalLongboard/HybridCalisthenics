const BASE_URL = "https://www.hybridcalisthenics.com";

export const FAMILY_SLUGS = {
  Pushups: "pushups",
  "Leg Raises": "legraises",
  Pullups: "pullups",
  Squats: "squats",
  Bridges: "bridges",
  Twists: "twists",
};

export const EXERCISE_SLUGS = {
  "Wall Pushups": "wall-pushups",
  "Incline Pushups": "incline-pushups",
  "Advanced Incline Pushups": "advanced-incline-pushups",
  "Knee Pushups": "knee-pushups",
  "Full Pushups": "full-pushups",
  "Narrow Pushups": "narrow-pushups",
  "Side-Staggered Pushups": "side-staggered-pushups",
  "Archer Pushups": "archer-pushups",
  "Sliding One-Arm Pushups": "sliding-onearm-pushups",
  "One Arm Pushups": "onearm-pushups",
  "Advanced One-Arm Pushups": "advanced-onearm-pushups",

  "Knee Raises": "knee-raises",
  "Advanced Knee Raises": "advanced-knee-raises",
  "Alternating Leg Raises": "alternating-leg-raises",
  "Full Leg Raises": "full-leg-raises",
  "Tuck Plow Raises": "tuck-plow-raises",
  "Plow Raises": "plow-raises",
  "Hanging Knee Raises": "hanging-knee-raises",
  "Advanced Hanging Knee Raises": "advanced-hanging-knee-raises",
  "Hanging Leg Raises": "hanging-leg-raises",
  "Toe to Bars": "toe-to-bars",

  "Wall Pullups": "wall-pullups",
  "Horizontal Pullups": "horizontal-pullups",
  "Advanced Horizontal Pullups": "advanced-horizontal-pullups",
  "Jackknife Pullups": "jackknife-pullups",
  "Full Pullups": "full-pullups",
  "Narrow Pullups": "narrow-pullups",
  "One Hand Pullups": "one-hand-pullups",
  "Advanced One Hand Pullups": "advanced-onehand-pullups",
  "Archer Pullups": "archer-pullups",
  "One Arm Pullups": "one-arm-pullups",

  "Jackknife Squats": "jackknife-squats",
  "Assisted Squats": "assisted-squats",
  "Half Squats": "half-squats",
  "Full Squats": "full-squats",
  "Narrow Squats": "narrow-squats",
  "Side Staggered Squats": "side-staggered-squats",
  "Front Staggered Squats": "front-staggered-squats",
  "Assisted One Leg Squats": "assisted-oneleg-squats",
  "One Leg Chair Squats": "one-leg-chair-squats",
  "One Leg Squats": "oneleg-squats",

  "Glute Bridges": "glute-bridges",
  "Straight Bridges": "straight-bridges",
  "Wall Bridges": "wall-bridges",
  "Incline Bridges": "incline-bridges",
  "Head Bridges": "head-bridges",
  "Full Bridges": "full-bridges",
  "Wheel Bridges": "wheel-bridges",
  "Tap Bridges": "tap-bridges",
  "Wall Walking Bridges": "wallwalking-bridges",
  "Stand to Stand Bridges": "standtostand-bridges",

  "Straight Leg Twists": "straight-leg-twists",
  "Bent Leg Twists": "bent-leg-twists",
  "Full Twists": "full-twists",
};

export function familyLink(familyName) {
  const slug = FAMILY_SLUGS[familyName];
  if (!slug) return familyName;
  return `<a href="${BASE_URL}/${slug}" target="${slug}">${familyName}</a>`;
}

export function exerciseLink(exerciseName) {
  const slug = EXERCISE_SLUGS[exerciseName];
  if (!slug) return exerciseName;
  return `<a href="${BASE_URL}/${slug}" target="${slug}">${exerciseName}</a>`;
}
