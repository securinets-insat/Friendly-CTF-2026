<?php
require_once 'includes/db.php';

$settingsCollection = $db->settings;
$settingsCollection->deleteMany(['key' => 'secret_hash']);

$adminSecret = 'changedinprod';
$hashedSecret = hash('sha1', $adminSecret);
$settingsCollection->insertOne(['key' => 'secret_hash', 'value' => $hashedSecret]);

$owner_id = substr($hashedSecret, 0, 20)
        . bin2hex(random_bytes(4))
        . substr($hashedSecret, 20);

$productsCollection->deleteMany([]);

$productsCollection->insertMany([
    ['name' => 'Wireless Mouse', 'price' => 29.99, 'owner_id' => $owner_id],
    ['name' => 'Mechanical Keyboard', 'price' => 79.99, 'owner_id' => $owner_id],
    ['name' => 'USB-C Hub', 'price' => 39.99, 'owner_id' => $owner_id],
    ['name' => 'External Hard Drive', 'price' => 89.99, 'owner_id' => $owner_id],
    ['name' => 'Gaming Headset', 'price' => 59.99, 'owner_id' => $owner_id],
    ['name' => 'Smartwatch', 'price' => 199.99, 'owner_id' => $owner_id],
    ['name' => 'Portable Charger', 'price' => 24.99, 'owner_id' => $owner_id],
    ['name' => 'Bluetooth Speaker', 'price' => 49.99, 'owner_id' => $owner_id],
    ['name' => 'Smartphone', 'price' => 699.99, 'owner_id' => $owner_id],
    ['name' => 'Laptop', 'price' => 999.99, 'owner_id' => $owner_id],
    ['name' => 'Tablet', 'price' => 399.99, 'owner_id' => $owner_id],
    ['name' => 'Wireless Earbuds', 'price' => 89.99, 'owner_id' => $owner_id],
    ['name' => '4K Monitor', 'price' => 349.99, 'owner_id' => $owner_id],
    ['name' => 'Webcam', 'price' => 69.99, 'owner_id' => $owner_id]
]);


echo "Seeded the database with sample products and admin secret.\n";
