import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const userId = util.autoId();
  return {
    operation: 'PutItem',
    key: {
      id: util.dynamodb.toDynamoDB(userId)
    },
    attributeValues: {
      id: util.dynamodb.toDynamoDB(userId),
      name: util.dynamodb.toDynamoDB(ctx.arguments.email),
      email: util.dynamodb.toDynamoDB(ctx.arguments.email),
      createdAt: util.dynamodb.toDynamoDB(util.time.nowISO8601())
    },
    condition: {
      expression: 'attribute_not_exists(email)'
    }
  };
}

export function response(ctx) {
  if (ctx.error) {
    return util.error(ctx.error.message, ctx.error.type);
  }
  return ctx.result;
}
