# Retail Demo Store CloudFormation Templates

This readme explains the use and utility of each of the listed CloudFormation stacks and its resources.

<h3>Template list</h3>
<details><summary>expand / collapse</summary>

- [**base/**](#base)
- [**event-engine/**](#ee)
- **services/**
- alexa.yaml
- amazonpay.yaml
- apigateway.yaml
- cleanup-bucket.yaml
- deployment-support.yaml
- lex.yaml
- location.yaml
- mparticle.yaml
- segment.yaml
- swagger-ui-pipeline.yaml
- template.yaml
- web-ui-pipeline.yaml

</details>

## base/ | Base infrastructure templates <a name="base"></a>

#### Purpose

These templates deploy infrastructure to support the Retail Demo Store.

[Find out more](./base)

## event-engine/ | AWS Event Engine templates <a name="ee"></a>

#### Purpose

These templates are needed by AWS' Event Engine to support running AWS-led workshop events.

## services/ | Retail Demo Store business service infrastructure <a name="services"></a>

#### Purpose

These are the infrastructure components to support the business services (i.e. Product, Search etc).

---

Go back to the [Retail Demo Store README](../../../README.md).

<!-- Template for future entries, don't forget to link in TOC.

## <a name="file-name"></a> file-name.yaml | Friendly name of the stack

Appropriate information about the stack, its purpose, and the resources it deploys. Think of this as the stack's readme.

-->
