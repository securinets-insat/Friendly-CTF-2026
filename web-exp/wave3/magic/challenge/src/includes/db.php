<?php
require_once __DIR__ . '/../vendor/autoload.php';

$mongoUri = getenv('MONGO_URI') ?: 'mongodb://localhost:27017';

$client = new MongoDB\Client($mongoUri);
$db = $client->mystore;
$productsCollection = $db->products;
$settingsCollection = $db->settings;
