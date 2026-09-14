FROM gcc:14 AS readflag
WORKDIR /build
COPY readflag.c .
RUN gcc -static -O2 -o readflag readflag.c



FROM php:8.3-apache

RUN apt-get update && apt-get install -y \
    libssl-dev \
    libmagickwand-dev \
    pkg-config \
    unzip \
    git \
    && pecl install mongodb imagick \
    && docker-php-ext-enable mongodb imagick \
    && apt-get remove -y pkg-config git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html
COPY src/ /var/www/html/

RUN composer install --no-dev --optimize-autoloader

COPY php.ini /usr/local/etc/php/conf.d/99-custom.ini

RUN chown -R root:root /var/www/html \
    && find /var/www/html -type d -exec chmod 0755 {} \; \
    && find /var/www/html -type f -exec chmod 0644 {} \; \
    && mkdir -p /var/www/html/uploads \
    && chown -R www-data:www-data /var/www/html/uploads \
    && find /var/www/html/uploads -type d -exec chmod 0755 {} \; \
    && find /var/www/html/uploads -type f -exec chmod 0644 {} \;

COPY flag.txt /flag.txt 
RUN chown root:root /flag.txt
RUN chmod 400 /flag.txt

COPY --from=readflag /build/readflag /usr/local/bin/readflag
  RUN chown root:root /usr/local/bin/readflag \
      && chmod 4111 /usr/local/bin/readflag

RUN { \
    echo '<Directory /var/www/html/uploads>'; \
    echo '    Options -Indexes'; \
    echo '    <FilesMatch "\.(php|phtml|php3|php4|php5|pl|py|cgi|sh)$">'; \
    echo '        Require all denied'; \
    echo '    </FilesMatch>'; \
    echo '</Directory>'; \
    } > /etc/apache2/conf-available/uploads-hardening.conf \
    && a2enconf uploads-hardening

EXPOSE 80
