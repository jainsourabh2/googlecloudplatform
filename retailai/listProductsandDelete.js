//https://github.com/googleapis/nodejs-retail/tree/main/samples/generated/v2 

'use strict';

function main() {
  // [START retail_v2_generated_ProductService_ListProducts_async]
  /**
   * TODO(developer): Uncomment these variables before running the sample.
   */
  /**
   *  Required. The parent branch resource name, such as
   *  `projects/* /locations/global/catalogs/default_catalog/branches/0`. Use
   *  `default_branch` as the branch ID, to list products under the default
   *  branch.
   *  If the caller does not have permission to list
   *  Product google.cloud.retail.v2.Product s under this branch, regardless of
   *  whether or not this branch exists, a PERMISSION_DENIED error is returned.
   */
   const parent = 'projects/<<projectid>>/locations/global/catalogs/default_catalog/branches/0'
  /**
   *  Maximum number of Product google.cloud.retail.v2.Product s to return. If
   *  unspecified, defaults to 100. The maximum allowed value is 1000. Values
   *  above 1000 will be coerced to 1000.
   *  If this field is negative, an INVALID_ARGUMENT error is returned.
   */
   const pageSize = 2
  /**
   *  A page token
   *  ListProductsResponse.next_page_token google.cloud.retail.v2.ListProductsResponse.next_page_token,
   *  received from a previous
   *  ProductService.ListProducts google.cloud.retail.v2.ProductService.ListProducts
   *  call. Provide this to retrieve the subsequent page.
   *  When paginating, all other parameters provided to
   *  ProductService.ListProducts google.cloud.retail.v2.ProductService.ListProducts
   *  must match the call that provided the page token. Otherwise, an
   *  INVALID_ARGUMENT error is returned.
   */
  // const pageToken = 'abc123'
  /**
   *  A filter to apply on the list results. Supported features:
   *  * List all the products under the parent branch if
   *  filter google.cloud.retail.v2.ListProductsRequest.filter  is unset.
   *  * List Product.Type.VARIANT google.cloud.retail.v2.Product.Type.VARIANT
   *  Product google.cloud.retail.v2.Product s sharing the same
   *    Product.Type.PRIMARY google.cloud.retail.v2.Product.Type.PRIMARY
   *    Product google.cloud.retail.v2.Product. For example:
   *      `primary_product_id = "some_product_id"`
   *  * List Product google.cloud.retail.v2.Product s bundled in a
   *  Product.Type.COLLECTION google.cloud.retail.v2.Product.Type.COLLECTION
   *  Product google.cloud.retail.v2.Product.
   *    For example:
   *      `collection_product_id = "some_product_id"`
   *  * List Product google.cloud.retail.v2.Product s with a partibular type.
   *  For example:
   *      `type = "PRIMARY"`
   *      `type = "VARIANT"`
   *      `type = "COLLECTION"`
   *  If the field is unrecognizable, an INVALID_ARGUMENT error is returned.
   *  If the specified
   *  Product.Type.PRIMARY google.cloud.retail.v2.Product.Type.PRIMARY
   *  Product google.cloud.retail.v2.Product  or
   *  Product.Type.COLLECTION google.cloud.retail.v2.Product.Type.COLLECTION
   *  Product google.cloud.retail.v2.Product  does not exist, a NOT_FOUND error
   *  is returned.
   */
  // const filter = 'abc123'
  /**
   *  The fields of Product google.cloud.retail.v2.Product  to return in the
   *  responses. If not set or empty, the following fields are returned:
   *  * Product.name google.cloud.retail.v2.Product.name
   *  * Product.id google.cloud.retail.v2.Product.id
   *  * Product.title google.cloud.retail.v2.Product.title
   *  * Product.uri google.cloud.retail.v2.Product.uri
   *  * Product.images google.cloud.retail.v2.Product.images
   *  * Product.price_info google.cloud.retail.v2.Product.price_info
   *  * Product.brands google.cloud.retail.v2.Product.brands
   *  If "*" is provided, all fields are returned.
   *  Product.name google.cloud.retail.v2.Product.name  is always returned no
   *  matter what mask is set.
   *  If an unsupported or unknown field is provided, an INVALID_ARGUMENT error
   *  is returned.
   */
  // const readMask = {}

  // Imports the Retail library
  const {ProductServiceClient} = require('@google-cloud/retail').v2;

  // Instantiates a client
  const retailClient = new ProductServiceClient();

  async function callListProducts() {
    // Construct request
    const request = {
      parent,
    };

    // Run request
    const iterable = await retailClient.listProductsAsync(request);
    for await (const response of iterable) {
        console.log(response.id);
        let name = 'projects/<<projectid>>/locations/global/catalogs/default_catalog/branches/0/products/'+response.id
        let request = {
            name,
        };
        try{
            let response = await retailClient.deleteProduct(request);
        }catch(error){
            console.log(error)
        }
    }
  }

  callListProducts();
}

process.on('unhandledRejection', err => {
  console.error(err.message);
  process.exitCode = 1;
});
main(...process.argv.slice(2));
