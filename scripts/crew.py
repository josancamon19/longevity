import os

from crewai import Agent, Crew, Task
from crewai_tools.tools.directory_read_tool.directory_read_tool import DirectoryReadTool
from crewai_tools.tools.file_read_tool.file_read_tool import FileReadTool

os.environ["OPENAI_MODEL_NAME"] = 'o1-mini'

personal_trainer_agent = Agent(
    role="Olympiads Personal Trainer",
    goal=(
        "Tailor training plans to clients' unique needs and "
        "preferences to help them achieve their fitness goals."
    ),
    verbose=True,
    backstory=(
        '''
        As an Olympiads personal trainer, you have a reputation for delivering results. 
        Clients (Busy entrepreneurs) trust you to help them achieve their fitness goals,
        through data-driven training plans tailored to their unique needs and preferences.

        You based your training philosophy on data and latest research, and you are always looking for new ways to improve your clients' performance and well-being.
        You dive deep into your clients' training history, nutritional data, and other relevant information to identify patterns and insights that can inform your personalized planning,
        and ask dozens of questions to understand their goals, preferences, and constraints, to fully know them in depth.
        '''
    )
)

nutritionist_agent = Agent(
    role="Nutritionist Lead",
    goal=(
        "Design and implement nutrition plans for Olympiads Personal Trainer Agent clients."
    ),
    verbose=True,
    backstory=(
        '''
        Having worked as a nutritionist for Olympiads for years, you have a deep understanding of the relationship between nutrition and fitness.
        You have helped hundreds of clients achieve their fitness goals by designing and implementing personalized nutrition plans that align with their training goals, schedule, and preferences.

        You are passionate about using data and research to inform your recommendations, and you are always looking for new ways to optimize your clients' performance and well-being.
        '''
    )
)

list_available_information = DirectoryReadTool(
    directory='data',
    name='List Available Client\'s Information Files',
    description='List all available information files about the client.',
    verbose=True,
)

file_read_tool = FileReadTool()

understand_client_task = Task(
    description='Read and understand all the available client\'s information files.',
    agent=personal_trainer_agent,
    expected_output='A 100 word summary of the client, their goals, preferences, and constraints.',
    tools=[list_available_information, file_read_tool],
    verbose=True,
    human_input=False,
)

create_training_plan_task = Task(
    description='Create a super personalized training plan for the client, based on the information provided.',
    agent=personal_trainer_agent,
    expected_output='''
    A detailed workout plan, that contains:
    Exercise name, Sets, Reps, Rest time, RPE, progression plan, notes.

    The plan should be tailored to the client's goals, preferences, and constraints.
    Should be an 8-week plan.
    It should include goals for each phase, and how the plan will evolve over time.
    For example, aiming strength gain by the end. 

    Include a brief explanation of the decision-making process behind the plan.
    Do not include any nutrition-related information.

    Output a markdown table with the plan.
    ''',
    output_file='training.md',
    verbose=True,
    human_input=True
)

nutrition_task = Task(
    description='Develop a personalized nutrition plan for the client.',
    agent=nutritionist_agent,
    expected_output='A detailed nutrition plan, including daily caloric intake, macronutrient distribution, meal timing.',
    verbose=True,
    human_input=True
)

crew = Crew(
    agents=[personal_trainer_agent, ],
    tasks=[understand_client_task, create_training_plan_task, ],
    verbose=True,
    memory=True,
)

# NEXT STEPS
# TODO: Be able to chat with trainer agent, before moving to nutritionist, not just single verification.

# - Better output from Trainer into nutritionist, also nutritionist doesn't know shit about the user when called.
# - Nutritionist is outputing meals, it shouldn't, output only macros.
# - Nutritionist should have access to available meals csv + nutrition details.

# - Final agent that presents this into a table or markdown file, that can be imported into notion.

# Next steps
# - How to chat, and iterate with a specific one?
# - Is it more useful than previous one?
# - How better it get's with o1 mini or o1 preview?
# - should have a training lead / manager? that oversees to each agent? hierarchy?
# - Jeff nippard agent? 👀 Jeremy either agent? would be fun


# - Longevity agents?
# - DNA access, bloodwork access, and aging pace scores :/

if __name__ == '__main__':
    crew_output = crew.kickoff()
    print(crew.usage_metrics)
