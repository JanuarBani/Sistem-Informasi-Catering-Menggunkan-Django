(function ($) {
  "use strict";

  var OptionManager = (function () {
    var objToReturn = {};
    var defaultOptions = {
      classCartIcon: "my-cart-icon",
      classCartBadge: "my-cart-badge",
      affixCartIcon: true,
      checkoutCart: function (products) {},
      clickOnAddToCart: function ($addTocart) {},
      getDiscountPrice: function (products) {
        return null;
      },
    };

    var getOptions = function (customOptions) {
      var options = $.extend({}, defaultOptions);
      if (typeof customOptions === "object") {
        $.extend(options, customOptions);
      }
      return options;
    };

    objToReturn.getOptions = getOptions;
    return objToReturn;
  })();

  var ProductManager = (function () {
    var objToReturn = {};

    localStorage.products = localStorage.products ? localStorage.products : "";
    var getIndexOfProduct = function (id) {
      var productIndex = -1;
      var products = getAllProducts();
      $.each(products, function (index, value) {
        if (value.id == id) {
          productIndex = index;
          return;
        }
      });
      return productIndex;
    };
    var setAllProducts = function (products) {
      localStorage.products = JSON.stringify(products);
    };
    var addProduct = function (id, name, summary, price, quantity, image) {
      var products = getAllProducts();
      products.push({
        id: id,
        name: name,
        summary: summary,
        price: price,
        quantity: quantity,
        image: image,
      });
      setAllProducts(products);
    };

    var getAllProducts = function () {
      try {
        var products = JSON.parse(localStorage.products);
        return products;
      } catch (e) {
        return [];
      }
    };

    var updateProduct = function (id, quantity) {
      var productIndex = getIndexOfProduct(id);
      if (productIndex < 0) {
        return false;
      }
      var products = getAllProducts();
      products[productIndex].quantity =
        typeof quantity === "undefined"
          ? products[productIndex].quantity * 1 + 1
          : quantity;
      setAllProducts(products);
      return true;
    };

    objToReturn.getAllProducts = getAllProducts;
    objToReturn.updateProduct = updateProduct;
    objToReturn.addProduct = addProduct;
    return objToReturn;
  })();

  var goToCartIcon = function ($addTocartBtn) {
    var $cartIcon = $(".my-cart-icon");
    var $image = $(
      '<img width="30px" height="30px" src="' +
        $addTocartBtn.data("image") +
        '"/>'
    ).css({ position: "fixed", "z-index": "999" });
    $addTocartBtn.prepend($image);
    var position = $cartIcon.position();
    $image.animate(
      {
        top: position.top,
        left: position.left,
      },
      500,
      "linear",
      function () {
        $image.remove();
      }
    );
  };

  $(document).ready(function () {
    var $cartBadge = $(".my-cart-badge");

    $(".add-to-cart").click(function () {
      var $button = $(this);
      var id = $button.data("id");
      var name = $button.data("name");
      var price = $button.data("price");
      var image = $button.data("image");
      var quantity = 1; // Default quantity

      ProductManager.addProduct(id, name, "", price, quantity, image);
      $cartBadge.text(ProductManager.getAllProducts().length);

      goToCartIcon($button);
    });
  });
})(jQuery);
