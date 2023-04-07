from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from hugoai.rules import RULES

#llm = ChatOpenAI(model_name="gpt-4", temperature=0.0)
llm = OpenAI(temperature=0.0)


template_utterance_expander = """
Below is a conversation context comprising a conversation thread and a selected utterance.
Elaborate on what the selected utterance actually means in the context of what was already stated in the conversation thread.
Specifically, elaborate on all the referring expressions and what they could mean.
Focus on explicating if words have negative or positive connotations in this context, and what/who group (mentioned previously in context) they refer to.
Remember, words might specific (even unusual) meaning in this particular context, different from other contexts. For example animals and inanimate objects may actually refer to groups or types of people.

\n\n CONVERSATION CONTEXT: \n
    Thread:\n{thread}\n
    Selected Utterance: \n{utterance}\n
    Deeper Meaning of selected utterance:
"""

prompt_utterance_expander = PromptTemplate(
    input_variables=["thread","utterance"],
    template=template_utterance_expander,
)

chain_utterance_expander = LLMChain(llm=llm, prompt=prompt_utterance_expander)


##################

template_rule_checker="""
 Below is a conversation context comprising a set of forum rules, a conversation thread, a selected utterance and its deeper meaning.
 Go through each rule and identify specifically any and all (if any) rules that are either exemplified (in a positive prosocial way) or violated (in a negative antisocial way) by the selected utterance when understood in context of the rest of the conversation thread. Also explain why/how it exemplifies or violates. When you identify a rule violation/exemplifcation remember to highlight the one rule that is the MOST relevant to the selected utterance.

    \n\n CONVERSATION CONTEXT: \n
    Rules: \n{rules}\n
    Conversation thread: \n{thread}\n
    Selected Utterance: {utterance}\n
    Deeper meaning: {meaning}\n
    Rule exemplifcation/violation:
"""

prompt_rule_checker = PromptTemplate(
    input_variables=["rules","thread","utterance", "meaning"],
    template=template_rule_checker,
)

chain_rule_checker = LLMChain(llm=llm, prompt=prompt_rule_checker)

##########################


template_dsr="""
Below is a conversation context comprising a conversation thread, a selected utterance and its deeper meaning.
Identify if the user (author) of the selected utterance is targeting "social regard" towards a particular group of people.
The "social regard" could be positive (like empathy, respect, helpfulness) or negative (like contempt, dehumanization, harming).
Identify the specific group being targeted as well as the type of social regard directed towards the group.

\n\n CONVERSATION CONTEXT: \n
    Thread:\n{thread}\n
    Selected Utterance: \n{utterance}\n
    Deeper Meaning: \n{meaning}\n
    Directed Social Regard toward a particular Group of people:
"""

prompt_dsr = PromptTemplate(
    input_variables=["thread","utterance", "meaning"],
    template=template_dsr,
)

chain_dsr = LLMChain(llm=llm, prompt=prompt_dsr)

############################

template_respond="""
 Below is a conversation context comprising a set of forum rules, a conversation thread, a selected utterance, its deeper meaning, and an analysis of whether the selected utterance violated or exemplified any rules.
 If any of the rules are exemplified or violated, generate a response to the selected utterance identifying the most relevant rule.
 Your response to a selected utterance(if you deem one to be necessary) should either REWARD the user for a rule exemplifying utterance or WARN the user of a forum violation (including specifying which rule they are violating) whichever is applicable to the utterance.
 When the user of the selected utterance is displaying negative social regard towards a group, your response must remind the user of what qualities, desires, beliefs, intentions, morals or values they share in common with the targeted group.
 Your response should address the user of the selected utterance, match the linguistic style of the thread, and must display prosocial qualities of empathy, compassion, and curiosity.

If no response is necessary, just say "<NONE>"

    \n\n CONVERSATION CONTEXT: \n
    Rules:\n{rules}\n
    Thread:\n{thread}\n
    Selected Utterance: \n{utterance}\n
    Deeper Meaning: \n{meaning}\n
    Directed Social regard towards a group: \n{dsr}\n
    Analysis: \n{analysis}\n
    Response:
"""

prompt_respond = PromptTemplate(
    input_variables=["thread","utterance", "analysis", "rules", "dsr", "meaning"],
    template=template_respond,
)

chain_respond = LLMChain(llm=llm, prompt=prompt_respond)

#########################

def respond(chat_history, rules):
    utterance = chat_history[-1]
    print(f"Utterance: {utterance}")
    print(f"Rules: \n{rules}\n")
    thread = "\n".join([f"[{item['user']}]: {item['text']}" for item in chat_history])
    meaning = chain_utterance_expander.run(thread=thread, utterance=utterance)
    print(f"Meaning: {meaning}")
    analysis = chain_rule_checker.run(rules=rules, thread=thread, utterance=utterance, meaning=meaning)
    print(f"Analysis: {analysis}")
    dsr = chain_dsr.run(thread=thread, utterance=utterance, meaning=meaning)
    print(f"DSR: {dsr}")
    response = chain_respond.run(rules=rules, thread=thread, utterance=utterance, analysis=analysis, dsr=dsr, meaning=meaning)
    print(f"Response: {response}")
    output = {'response': response,
              'utterance':utterance,
              'meaning': meaning,
              'analysis': analysis,
              'dsr': dsr}
    return output















