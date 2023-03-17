"""Supervisor of the Maze Runner benchmark."""

from controller import Supervisor
import os


def isPositionChanged(v1, v2):
    return abs(v1[1] - v2[1]) > 0.001 or abs(v1[0] - v2[0]) > 0.001


def isMazeEndReached(position):
    return position[0] < 0.15 and position[0] > -0.15 and position[1] > -0.60 and position[1] < -0.45


supervisor = Supervisor()
timestep = int(4 * supervisor.getBasicTimeStep())
supervisor.step(10 * timestep)

thymio2 = supervisor.getFromDef("THYMIO2")

supervisor.step(10 * timestep)

mazeBlocksList = []
mazeBlocksListCount = 0
topChildrenField = supervisor.getFromDef("MAZE_WALLS").getField("children")
topNodesCount = topChildrenField.getCount()
for i in range(topNodesCount):
    node = topChildrenField.getMFNode(i)
    if node.getTypeName() == "MazeBlock":
        object = {
            "node": node,
            "initialPosition": node.getPosition()
        }
        mazeBlocksList.append(object)
        mazeBlocksListCount += 1


running = True
stopMessageSent = False
while running and supervisor.step(timestep) != -1:
    time = supervisor.getTime()
    # If some of the maze blocks have been moved immediately terminate the benchmark
    for i in range(0, mazeBlocksListCount):
        item = mazeBlocksList[i]
        if isPositionChanged(item['initialPosition'], item['node'].getPosition()):
            time = 60
            supervisor.wwiSendText("time:%-24.3f" % time)
            break

    if time < 60 and not isMazeEndReached(thymio2.getPosition()):
        supervisor.wwiSendText("time:%-24.3f" % time)
    else:
        running = False
        timestep = int(timestep / 4)

supervisor.wwiSendText("stop_%-24.3f" % time)

# Performance output used by automated CI script
CI = os.environ.get("CI")
if CI:
    print(f"performance:{time}")

supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)
