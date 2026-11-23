// Turn a list into an object keyed by one field: [{id: 1}, {id: 2}] -> {1: {...}, 2: {...}}.
// Most slices store their data this way so components can look items up by id.
export const keyBy = (items, key = "id") =>
  Object.fromEntries(items.map((item) => [item[key], item]));
