export function request(ctx) {
  return {};
}

export function response(ctx) {
  return ctx.stash.userMessage || ctx.result;
}
