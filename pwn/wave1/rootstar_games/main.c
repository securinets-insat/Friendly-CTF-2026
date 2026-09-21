#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>


#define DEFAULT_USERNAME "RockstarSeniorSWE"
#define DEFAULT_PASSWORD "MyPasswordIsVeryV\x00eryStrong#@."
#define DEFAULT_ROLE "Developer"

typedef struct Account{
    char role[67];
    char username[67];
    char password[67];
}Account;

Account* account;


void setup(){
    setbuf(stdout,0);
    setbuf(stdin,0);
    setbuf(stderr,0);
    account = malloc(sizeof(Account));
    sprintf(account->username,DEFAULT_USERNAME);
    sprintf(account->password,DEFAULT_PASSWORD);
    sprintf(account->role,DEFAULT_ROLE);
}


void login() {
    printf("===============================================\n");
    printf("        ROCKSTAR GAMES - DEVELOPER PANEL v1\n");
    printf("===============================================\n");
    printf("\n");
    printf("Welcome to the Rockstar Developer Portal.\n");
    printf("Internal system - Authorized personnel only.\n");
    printf("\n");
    printf("[!] Default developer credentials detected:\n");
    printf("    Username : ??????????????\n");
    printf("    Password : ??????????????\n");
    printf("\n");
    printf("===============================================\n");
    printf("        GTA VI DEVELOPMENT ENVIRONMENT\n");
    printf("===============================================\n");
    printf("\n");
    printf("Enter credentials to continue...\n");
    Account* acc=account;
    char username[67];
    char password[67];
    read(0,username,66);
    read(0,password,66);
    if(strcmp(username,acc->username)==0 && strcmp(password,acc->password)==0){
        return;
    }
    printf("Invalid Credentials!\n");
    printf("Exiting...\n");
    exit(0);
}


void showTopSecretAssest(){
    system("cat flag");
}

void challenge(){
    login();
    printf("Welcome mr Developer");
    printf("Please write your completed tasks today:\n");
    printf("> ");
    char buf[67];
    read(0,buf,65);
    char result[67+sizeof("Saved! Your completed tasks are:")];
    sprintf(result,"Saved! Your completed tasks are: %s",buf);
    printf(result);
    printf("Thank you!\n");
    if(strcmp("CEO",account->role)==0){
        showTopSecretAssest();
    }
    printf("Logging out...");

    exit(0);

}


void main(){
    setup();
    challenge();
    exit(0);
}