import enum


class NodeType(enum.Enum):
    Start = 0
    Exit = 1
    Cond = 2
    Loop = 3
    Normal = 4


class Node:
    id = None
    content = None
    nextNode = None
    previousNode = None
    currentMergeNode = None
    parentMergeNode = None
    nodeType = NodeType.Normal
    mergeNode = False
    children = []
    visited = False

    def __init__(self, id, content, previousNode, currentMergeNode, parentMergeNode, nodeType=NodeType.Normal,
                 mergeNode=False):
        self.id = id
        self.content = content
        self.previousNode = previousNode
        self.currentMergeNode = currentMergeNode
        self.parentMergeNode = parentMergeNode
        self.nodeType = nodeType
        self.mergeNode = mergeNode

    def addChild(self, node):
        self.children.append(node)

    def isMergeNode(self):
        return self.mergeNode

    def isVisited(self):
        return self.visited

    def setVisited(self, visited=True):
        self.visited = visited

    def __str__(self):
        return 'ID: ' + str(self.id) + '\nType: ' + str(self.nodeType) + '\nContent: '+str(self.content)


class CodeParser:
    graph = None

    def parseCode(self, code: str):
        counter = 1

        tempCurrentMergeNode = None
        tempParentMergeNode = None
        tempPreviousNode = None

        self.graph = Node(counter, "Start", None, None, None, NodeType.Start, False)
        counter += 1
        tempPreviousNode = self.graph

        exitNode = Node(counter, "Exit", None, None, None, NodeType.Exit, False)
        counter += 1

        lines = code.strip().split('\n')

        for i in range(len(lines)):
            line = lines[i].strip()

            if line == '':
                continue


            if line.startswith('if'):
                mNode = Node(counter, "Conditional merge point", tempPreviousNode, tempCurrentMergeNode, tempParentMergeNode, NodeType.Cond,
                             True)
                counter += 1

                tempParentMergeNode = tempCurrentMergeNode
                tempCurrentMergeNode = mNode

                curNode = Node(counter, line, tempPreviousNode, mNode, tempCurrentMergeNode, NodeType.Cond)
                tempCurrentMergeNode.addChild(curNode)

                tempPreviousNode.nextNode = mNode
                tempPreviousNode = curNode

            elif line.startswith('}') and (line.__contains__('else if') or line.__contains__('else')):
                curNode = Node(counter, line, tempPreviousNode, tempCurrentMergeNode, tempParentMergeNode,
                               NodeType.Cond)

                tempCurrentMergeNode.addChild(curNode)

                tempPreviousNode = curNode

            elif line.startswith('}'):
                if i + 1 == len(lines):
                    tempCurrentMergeNode.nextNode = exitNode

                # make the next node of the previous conditional the mergeNode's next node
                tempPreviousNode.nextNode = tempCurrentMergeNode.nextNode
                tempPreviousNode = tempCurrentMergeNode

                tempCurrentMergeNode = tempParentMergeNode
                tempParentMergeNode = tempCurrentMergeNode.parentMergeNode if tempCurrentMergeNode is not None else None

            else:
                curNode = Node(counter, line, tempPreviousNode, tempCurrentMergeNode, tempParentMergeNode,
                               NodeType.Normal)

                curNode.nextNode = exitNode

                tempPreviousNode.nextNode = curNode

                tempPreviousNode = curNode

            counter += 1

    def changeConditionalNextNode(self, mergeNode, gNextNode):
        for node in mergeNode.children:
            nextNode = node.nextNode

            while nextNode is not None:
                nextNode = node.nextNode
                #print(nextNode)

            node.nextNode = gNextNode

    def traverse(self):
        continueTraverse = True

        paths = []
        while continueTraverse:
            nextNode = self.graph
            path = [nextNode]
            while True:
                if nextNode.isMergeNode():
                    notVisited = 0
                    for node in nextNode.children:
                        if not node.isVisited():
                            notVisited += 1
                            nextNode = node
                            node.setVisited()
                            break

                    if notVisited == 0:
                        continueTraverse = False
                        break

                elif nextNode.nodeType == NodeType.Exit:
                    break

                else:
                    nextNode = nextNode.nextNode

                path.append(nextNode)

            if len(path) > 2:
                paths.append(path)

        return paths

    def printPath(self, paths):
        for path in paths:
            for node in path:
                print("Node: ", node.id, " - Content: ", node.content)

            print("\n")

# sample code
c = '''
    if(a>0){
        System.out.println("Hi");
    } else if{
        System.out.println("Hello");
    } else{
        System.out.println("Good Bye");
        System.out.println("Bye");
    }
'''
par = CodeParser()

par.parseCode(c)

par.printPath(par.traverse())