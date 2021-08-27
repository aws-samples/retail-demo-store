# Amazon Pay Integration

Amazon Pay is one of many online payment services that offer low friction,
secure checkout across different platforms. There is a partial integration of
<a href="sellercentral.amazon.com/">Amazon Pay for merchants</a>
into the Retail Demo Store.
    
If you enter your Amazon Pay credentials as parameters into CloudFormation when
deploying or updating this demo, an Amazon Pay button will be generated for you,
signed with those credentials. This Amazon Pay button allows users to intitate a
checkout session with your Amazon Pay store as the seller.


**Note:** *This is a partial integration that does not cover the full checkout process.
We go as far as initiating a checkout session which you can test by logging in with a sandbox user.*

## How to Set up Amazon Pay Integration

In order to set up the integration so that you can initiate a checkout session, we need to set up an
Amazon Pay merchant account, as well as a store, and obtain the integration credentials for that store. Having
obtained these credentials we can supply them to Retail Demo Store so that it can start a credentialed
checkout session which you can enter by authenticating a test user. For more information about integrating
with Amazon Pay see <a href="https://developer.amazon.com/docs/amazon-pay-checkout/get-set-up-for-integration.html">
these instructions</a>.

Here are step-by-step instructions to get you started with Amazon Pay in the Retail Demo Store:
<ol>
  <li>Set up an Amazon Pay account at <a href="https://sellercentral.amazon.com/">
    https://sellercentral.amazon.com/</a>.
  </li>
  <li>Select your sandbox testing account and create a test account as explained
    <a href="https://developer.amazon.com/docs/amazon-pay-checkout/amazon-pay-sandbox-accounts.html">
      here</a>. This test account will be different to your merchant account. For example, your main
    account may be <span class="code-text">RetailDemoStore@gmail.com</span> and your test user may be
    <span class="code-text">Brian@test.com</span>. This test user will be used to take on the role of a shopper
    checking out on the store.
  </li>
  <li>Obtain your account's integration details as described
    <a href="https://developer.amazon.com/docs/amazon-pay-checkout/get-set-up-for-integration.html#5-get-your-public-key-id">
      here</a>. The details you will need to obtain from the "Integration Central" hub in Seller Central are:
    <ul>
      <li>Your merchant ID.</li>
      <li>Your store ID.</li>
      <li>Your public API key ID.</li>
      <li>Your private key (this will be downloaded as a <tt>.pem</tt> file).</li>
    </ul>
  </li>
  <li>
    If creating a new deployment of Retail Demo Store, enter this information as parameters when deploying your
    CloudFormation template. If updating a deployment, follow the process for updating and enter
    this information as parameters when re-deploying your CloudFormation template.
     
     Note: Using the CloudFormation UI you will need to copy the contents of the private key .pem file into the pivate key parameter text field.
  </li>
  <li>
    If all is going well, the Amazon Pay button will show up on the checkout page. Note that this button will
    initiate an Amazon Pay session but will not receive any callbacks from Amazon Pay to continue the checkout.
    Instead, you will be redirected to the Amazon Pay developer pages and the purchase will be automatically
    accepted by Retail Demo Store.
  </li>
</ol>
