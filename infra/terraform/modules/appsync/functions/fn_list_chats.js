import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const query = {
    operation: 'Query',
    query: {
      expression: 'userId = :userId',
      expressionValues: {
        ':userId': util.dynamodb.toDynamoDB(ctx.arguments.userId)
      }
    },
    index: 'GSI1',
    scanIndexForward: false,
    limit: ctx.arguments.limit || 50
  };

  if (ctx.arguments.nextToken) {
    query.nextToken = ctx.arguments.nextToken;
  }

  return query;
}

export function response(ctx) {
  if (ctx.error) {
    return util.error(ctx.error.message, ctx.error.type);
  }
  return ctx.result.items;
}
