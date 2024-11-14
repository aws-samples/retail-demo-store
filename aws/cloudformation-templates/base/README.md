# Retail Demo Store Base Templates

This readme explains the use and utility of each of the listed CloudFormation stacks and its resources.

<h3>Template list</h3>
<details><summary>expand / collapse</summary>

- \_template.yaml
- authentication.yaml
- buckets.yaml
- cloudfront.yaml
- codecommit.yaml
- ecs-cluster.yaml
- [event-driven.yaml](#event-driven)
- notebook.yaml
- opensearch.yaml
- personalize.yaml
- servicediscovery.yaml
- ssm.yaml
- tables.yaml
- vpc.yaml

</details>

## event-driven.yaml | Event-Driven Architecture <a name="event-driven"></a>

#### Purpose

This stack adds the foundation resources to support [event-driven architecture](https://serverlessland.com/event-driven-architecture/intro) for the Retail Demo Store. One central [EventBridge event bus](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-bus.html) is created with some sensible default best practices, where producers can write [events](https://serverlessland.com/event-driven-architecture/event) to, and consumers can subscribe to them via [EventBridge rules](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-rules.html).

> 💡 **Remember!** Events represent a change in state of a business entity. Your service(s) should emit events, even if there are no known consumers of that event today.

#### Resources

| Resource               | CloudFormation Type             | Purpose                                                                                                                                                                                                                                                                              |
| ---------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🚌 Event Bus           | `AWS::Events::EventBus`         | The event bus where producers emit events to, and consumers consume from.                                                                                                                                                                                                            |
| 🗄️ Event Archive       | `AWS::Events::Archive`          | [EventBridge Archive](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-archive.html) will store a copy of events for a period of time so they can be replayed to downstream consumers if necessary. <br />**In this demo, the retention period is set to 120 days.**      |
| 🔎 Event Discoverer    | `AWS::EventSchemas::Discoverer` | [EventBridge Schemas](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-schema.html) will use the discoverer to document the schema of any events on the bus. This allows for self-documenting events, the creation of code bindings, and versioning of schemas over time. |
| 🎣 Catch-all Rule      | `AWS::Events::Rule`             | **Disabled by default** <br /> When enabled, this rule will send a JSON copy of all events on the bus to CloudWatch Logs. This can be useful for troubleshooting and gaining insight.                                                                                                |
| 🪵 Catch-all Log Group | `AWS::Logs::LogGroup`           | CloudWatch Log Group to serve as a target for the "catch-all" rule.                                                                                                                                                                                                                  |
| 🔒 IAM Role            | `AWS::IAM::Role`                | IAM role to allow EventBridge to send events directly to a CloudWatch Log Group when the "catch-all" rule is enabled.                                                                                                                                                                |
| ⚙️ SSM Parameter       | `AWS::SSM::Parameter`           | The name of the event bus resource will be unique per account. Storing it in [SSM Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) allows other services to ensure they are writing to the correct bus.           |

As well as storing the event bus name in SSM Parameter Store for future discovery, the value is also exported through CloudFormation for flexibility.

#### Making use of this component

**TODO:** Create Python event-wrapper with enterprise-wide metadata and document fully, link to those docs from here.

#### Further Learning

- [AWS Serverless Developer Advocate site](https://serverlessland.com)
- [AWS EDA Explained](https://aws.amazon.com/what-is/eda/)

---

Go back to the [Retail Demo Store README](../../../README.md).

<!-- Template for future entries, don't forget to link in TOC.

## <a name="file-name"></a> file-name.yaml | Friendly name of the stack

Appropriate information about the stack, its purpose, and the resources it deploys. Think of this as the stack's readme.

-->
