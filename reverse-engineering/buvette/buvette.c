#include <stdio.h>
#include <stdlib.h>

#define START_BUDGET 100.0
#define WATER_PRICE 500.0

void get_flag()
{
    FILE *flag_file;
    char flag[256];

    flag_file = fopen("flag.txt", "r");

    fgets(flag, sizeof(flag), flag_file);
    fclose(flag_file);

    printf("\n");
    printf("========================================\n");
    printf("       MABROUK! YOU GOT THE WATER!\n");
    printf("========================================\n");
    printf("FLAG: %s", flag);
    printf("========================================\n");
}

int main()
{
    double budget = START_BUDGET;
    int choice;
    int quantity;
    double total;

    printf("========================================\n");
    printf("          WELCOME TO BUVETTE INSAT\n");
    printf("========================================\n");
    printf("\n");
    printf("You are thirsty.\n");
    printf("The last bottles of water are almost gone.\n");
    printf("Unfortunately, you don't have enough money...\n");
    printf("Ezreb fissa3 w khoudh bayek .\n");
    printf("Ken techri lmee na3tik m3ah flag blech .\n");

    while (1)
    {
        printf("\n");
        printf("========================================\n");
        printf("             BUVETTE INSAT\n");
        printf("========================================\n");
        printf("Budget: %.2f DT\n", budget);
        printf("----------------------------------------\n");

        printf("1. Cappuccino          2.50 DT\n");
        printf("2. Express             2.00 DT\n");
        printf("3. Direct              3.00 DT\n");
        printf("4. Jus                 3.00 DT\n");
        printf("5. Pain au chocolat    2.00 DT\n");
        printf("6. Souffle             2.50 DT\n");
        printf("7. Pizza Thon          4.00 DT\n");
        printf("8. Pizza Jambon        3.50 DT\n");
        printf("9. Tor7 Billard        2.00 DT\n");
        printf("10. Mee Ma9tou3      500.00 DT\n");
        printf("11. Exit\n");

        printf("========================================\n");

        printf("\nChoose an option: ");

        if (scanf("%d", &choice) != 1)
        {
            printf("\nInvalid input.\n");

            while (getchar() != '\n')
                ;

            continue;
        }

        switch (choice)
        {
            case 1:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 2.50 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Cappuccino purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 2:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 2.00 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Express purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 3:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 3.00 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Direct purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 4:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 3.00 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Jus purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 5:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 2.00 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Pain au chocolat purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 6:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 2.50 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Souffle purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 7:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 4.00 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Pizza Thon purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 8:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity > 100)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 3.50 * quantity;

                if (budget >= total)
                {
                    budget -= total;

                    printf("%d x Pizza Jambon purchased!\n", quantity);
                    printf("Total: %.2f DT\n", total);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                    printf("Total required: %.2f DT\n", total);
                    printf("Current budget: %.2f DT\n", budget);
                }

                break;


            case 9:
                printf("Quantity: ");
                scanf("%d", &quantity);

                if (quantity <= 0 || quantity > 10)
                {
                    printf("Invalid quantity.\n");
                    break;
                }

                total = 2.00 * quantity;

                if (budget >= total)
                {
                    budget -= total;
                    printf("%d x Tor7 Billard purchased!\n", quantity);
                    printf("Remaining budget: %.2f DT\n", budget);
                }
                else
                {
                    printf("Not enough money.\n");
                }

                break;


            case 10:
                if (budget >= WATER_PRICE)
                {
                    budget -= WATER_PRICE;

                    printf("\nSa7a Baba!\n");
                    printf("You bought Mee Ma9tou3!\n");

                    get_flag();

                    return 0;
                }
                else
                {
                    printf("\nWalah Kezda Khouya!\n");
                    printf("Mee Ma9tou3 costs %.2f DT.\n",
                           WATER_PRICE);
                    printf("Current budget: %.2f DT\n", budget);
                }

                break;


            case 11:
                printf("\nGoodbye!\n");
                return 0;


            default:
                printf("\nInvalid option.\n");
                break;
        }
    }

    return 0;
}

