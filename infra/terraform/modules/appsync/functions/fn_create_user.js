import { util } from '@aws-appsync/utils';

export function request(ctx) {
  return {
    operation: 'PutItem',
    key: {
      id: util.dynamodb.toDynamoDB(ctx.identity.sub)
    },
    attributeValues: {
      id: util.dynamodb.toDynamoDB(ctx.identity.sub),
      name: util.dynamodb.toDynamoDB(ctx.arguments.email),
      email: util.dynamodb.toDynamoDB(ctx.arguments.email),
      createdAt: util.dynamodb.toDynamoDB(util.time.nowISO8601())
    },
    condition: {
      expression: 'attribute_not_exists(id)'
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    return util.error(ctx.error.message, ctx.error.type);
  }
  return ctx.result;
}
